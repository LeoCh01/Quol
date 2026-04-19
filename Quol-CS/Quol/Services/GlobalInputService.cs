using System;
using System.Collections.Generic;
using System.Linq;
using Avalonia.Threading;
using SharpHook;
using SharpHook.Data;

namespace Quol.Services;

/// <summary>
/// Global low-level keyboard and mouse hook service backed by SharpHook.
/// All public API uses friendly key name strings (e.g. "ctrl", "shift", "a", "f1")
/// matching the Python GlobalInputManager convention.
/// Hotkey combos are "+" joined: "ctrl+shift+h".
/// </summary>
public sealed class GlobalInputService : IDisposable
{
    // ── Key name map (KeyCode → friendly string) ──────────────────────────

    private static readonly Dictionary<KeyCode, string> KeyNames = new()
    {
        [KeyCode.VcEscape] = "esc",
        [KeyCode.VcF1] = "f1",
        [KeyCode.VcF2] = "f2",
        [KeyCode.VcF3] = "f3",
        [KeyCode.VcF4] = "f4",
        [KeyCode.VcF5] = "f5",
        [KeyCode.VcF6] = "f6",
        [KeyCode.VcF7] = "f7",
        [KeyCode.VcF8] = "f8",
        [KeyCode.VcF9] = "f9",
        [KeyCode.VcF10] = "f10",
        [KeyCode.VcF11] = "f11",
        [KeyCode.VcF12] = "f12",
        [KeyCode.Vc1] = "1",
        [KeyCode.Vc2] = "2",
        [KeyCode.Vc3] = "3",
        [KeyCode.Vc4] = "4",
        [KeyCode.Vc5] = "5",
        [KeyCode.Vc6] = "6",
        [KeyCode.Vc7] = "7",
        [KeyCode.Vc8] = "8",
        [KeyCode.Vc9] = "9",
        [KeyCode.Vc0] = "0",
        [KeyCode.VcA] = "a",
        [KeyCode.VcB] = "b",
        [KeyCode.VcC] = "c",
        [KeyCode.VcD] = "d",
        [KeyCode.VcE] = "e",
        [KeyCode.VcF] = "f",
        [KeyCode.VcG] = "g",
        [KeyCode.VcH] = "h",
        [KeyCode.VcI] = "i",
        [KeyCode.VcJ] = "j",
        [KeyCode.VcK] = "k",
        [KeyCode.VcL] = "l",
        [KeyCode.VcM] = "m",
        [KeyCode.VcN] = "n",
        [KeyCode.VcO] = "o",
        [KeyCode.VcP] = "p",
        [KeyCode.VcQ] = "q",
        [KeyCode.VcR] = "r",
        [KeyCode.VcS] = "s",
        [KeyCode.VcT] = "t",
        [KeyCode.VcU] = "u",
        [KeyCode.VcV] = "v",
        [KeyCode.VcW] = "w",
        [KeyCode.VcX] = "x",
        [KeyCode.VcY] = "y",
        [KeyCode.VcZ] = "z",
        [KeyCode.VcSpace] = "space",
        [KeyCode.VcEnter] = "enter",
        [KeyCode.VcBackspace] = "backspace",
        [KeyCode.VcTab] = "tab",
        [KeyCode.VcCapsLock] = "caps_lock",
        [KeyCode.VcDelete] = "delete",
        [KeyCode.VcInsert] = "insert",
        [KeyCode.VcHome] = "home",
        [KeyCode.VcEnd] = "end",
        [KeyCode.VcPageUp] = "page_up",
        [KeyCode.VcPageDown] = "page_down",
        [KeyCode.VcUp] = "up",
        [KeyCode.VcDown] = "down",
        [KeyCode.VcLeft] = "left",
        [KeyCode.VcRight] = "right",
        [KeyCode.VcPrintScreen] = "print_screen",
        [KeyCode.VcPause] = "pause",
        [KeyCode.VcLeftShift] = "shift",
        [KeyCode.VcRightShift] = "shift_r",
        [KeyCode.VcLeftControl] = "ctrl",
        [KeyCode.VcRightControl] = "ctrl_r",
        [KeyCode.VcLeftAlt] = "alt",
        [KeyCode.VcRightAlt] = "alt_r",
        [KeyCode.VcLeftMeta] = "meta",
        [KeyCode.VcRightMeta] = "meta_r",
        [KeyCode.VcSemicolon] = "semicolon",
        [KeyCode.VcEquals] = "equals",
        [KeyCode.VcComma] = "comma",
        [KeyCode.VcMinus] = "minus",
        [KeyCode.VcPeriod] = "period",
        [KeyCode.VcSlash] = "slash",
        [KeyCode.VcBackQuote] = "tilde",
        [KeyCode.VcOpenBracket] = "open_bracket",
        [KeyCode.VcBackslash] = "backslash",
        [KeyCode.VcCloseBracket] = "close_bracket",
        [KeyCode.VcQuote] = "quote",
        [KeyCode.VcNumPad0] = "num0",
        [KeyCode.VcNumPad1] = "num1",
        [KeyCode.VcNumPad2] = "num2",
        [KeyCode.VcNumPad3] = "num3",
        [KeyCode.VcNumPad4] = "num4",
        [KeyCode.VcNumPad5] = "num5",
        [KeyCode.VcNumPad6] = "num6",
        [KeyCode.VcNumPad7] = "num7",
        [KeyCode.VcNumPad8] = "num8",
        [KeyCode.VcNumPad9] = "num9",
        [KeyCode.VcNumPadMultiply] = "num_multiply",
        [KeyCode.VcNumPadAdd] = "num_add",
        [KeyCode.VcNumPadSubtract] = "num_subtract",
        [KeyCode.VcNumPadDecimal] = "num_decimal",
        [KeyCode.VcNumPadDivide] = "num_divide",
        [KeyCode.VcNumPadEnter] = "num_enter",
    };

    // Reverse map: friendly string → KeyCode (built once from KeyNames)
    private static readonly Dictionary<string, KeyCode> KeyCodes = KeyNames.ToDictionary(
        kv => kv.Value,
        kv => kv.Key,
        StringComparer.OrdinalIgnoreCase
    );

    private static string KeyName(KeyCode code) =>
        KeyNames.TryGetValue(code, out var name) ? name : code.ToString().ToLowerInvariant();

    private static KeyCode ParseKey(string name) =>
        KeyCodes.TryGetValue(name.Trim().ToLowerInvariant(), out var code)
            ? code
            : Enum.Parse<KeyCode>(name.Trim(), ignoreCase: true); // fallback to raw enum name

    // ── State ─────────────────────────────────────────────────────────────

    private readonly object _lock = new();
    private readonly HashSet<KeyCode> _pressedKeys = [];

    // hotkeys:  uid → (combo-set, callback, suppress)
    private readonly Dictionary<
        string,
        (HashSet<KeyCode> Keys, Action Callback, bool Suppress)
    > _hotkeys = new();

    // key listeners: uid → (callback, suppressed-keys)
    private readonly Dictionary<
        string,
        (Action<string> Callback, HashSet<KeyCode> Suppressed)
    > _keyPressListeners = new();
    private readonly Dictionary<
        string,
        (Action<string> Callback, HashSet<KeyCode> Suppressed)
    > _keyReleaseListeners = new();

    // mouse listeners
    private readonly Dictionary<string, Action<int, int>> _mouseMoveListeners = new();
    private readonly Dictionary<string, Action<int, int, string, bool>> _mouseClickListeners =
        new();

    private SimpleGlobalHook? _hook;

    // ── Public API ────────────────────────────────────────────────────────

    /// <summary>
    /// Register a hotkey combo using SharpHook KeyCode names joined by '+'.
    /// e.g. "VcLeftControl+VcLeftShift+VcH"
    /// Returns a uid to pass to <see cref="RemoveHotkey"/>.
    /// </summary>
    public string AddHotkey(string combo, Action callback, bool suppress = false)
    {
        var uid = Guid.NewGuid().ToString();
        var keys = ParseCombo(combo);
        lock (_lock)
            _hotkeys[uid] = (keys, callback, suppress);
        return uid;
    }

    public void RemoveHotkey(string uid)
    {
        lock (_lock)
            _hotkeys.Remove(uid);
    }

    /// <summary>Register a raw key-press listener. Callback receives the KeyCode name string.</summary>
    public string AddKeyPressListener(
        Action<string> callback,
        IEnumerable<string>? suppressed = null
    )
    {
        var uid = Guid.NewGuid().ToString();
        lock (_lock)
            _keyPressListeners[uid] = (callback, ParseKeySet(suppressed));
        return uid;
    }

    public void RemoveKeyPressListener(string uid)
    {
        lock (_lock)
            _keyPressListeners.Remove(uid);
    }

    /// <summary>Register a raw key-release listener.</summary>
    public string AddKeyReleaseListener(
        Action<string> callback,
        IEnumerable<string>? suppressed = null
    )
    {
        var uid = Guid.NewGuid().ToString();
        lock (_lock)
            _keyReleaseListeners[uid] = (callback, ParseKeySet(suppressed));
        return uid;
    }

    public void RemoveKeyReleaseListener(string uid)
    {
        lock (_lock)
            _keyReleaseListeners.Remove(uid);
    }

    /// <summary>Register a mouse-move listener. Callback receives (x, y).</summary>
    public string AddMouseMoveListener(Action<int, int> callback)
    {
        var uid = Guid.NewGuid().ToString();
        lock (_lock)
            _mouseMoveListeners[uid] = callback;
        return uid;
    }

    public void RemoveMouseMoveListener(string uid)
    {
        lock (_lock)
            _mouseMoveListeners.Remove(uid);
    }

    /// <summary>Register a mouse-click listener. Callback receives (x, y, button, pressed).</summary>
    public string AddMouseClickListener(Action<int, int, string, bool> callback)
    {
        var uid = Guid.NewGuid().ToString();
        lock (_lock)
            _mouseClickListeners[uid] = callback;
        return uid;
    }

    public void RemoveMouseClickListener(string uid)
    {
        lock (_lock)
            _mouseClickListeners.Remove(uid);
    }

    // ── Lifecycle ─────────────────────────────────────────────────────────

    public void Start()
    {
        if (_hook is not null)
            return;

        _hook = new SimpleGlobalHook(runAsyncOnBackgroundThread: true);
        _hook.KeyPressed += OnKeyPressed;
        _hook.KeyReleased += OnKeyReleased;
        _hook.MouseMoved += OnMouseMoved;
        _hook.MouseDragged += OnMouseMoved;
        _hook.MousePressed += OnMousePressed;
        _hook.MouseReleased += OnMouseReleased;

        _hook.RunAsync();
    }

    public void Stop()
    {
        if (_hook is null)
            return;
        _hook.KeyPressed -= OnKeyPressed;
        _hook.KeyReleased -= OnKeyReleased;
        _hook.MouseMoved -= OnMouseMoved;
        _hook.MouseDragged -= OnMouseMoved;
        _hook.MousePressed -= OnMousePressed;
        _hook.MouseReleased -= OnMouseReleased;
        _hook.Dispose();
        _hook = null;

        lock (_lock)
        {
            _hotkeys.Clear();
            _keyPressListeners.Clear();
            _keyReleaseListeners.Clear();
            _mouseMoveListeners.Clear();
            _mouseClickListeners.Clear();
            _pressedKeys.Clear();
        }
    }

    public void Dispose() => Stop();

    // ── Event handlers ────────────────────────────────────────────────────

    private void OnKeyPressed(object? sender, KeyboardHookEventArgs e)
    {
        var code = e.Data.KeyCode;
        var keyName = KeyName(code);
        bool suppress = false;

        lock (_lock)
            _pressedKeys.Add(code);

        foreach (var (_, (keys, cb, supp)) in Snap(_hotkeys))
        {
            if (_pressedKeys.IsSupersetOf(keys))
            {
                Dispatch(cb);
                if (supp)
                    suppress = true;
            }
        }

        foreach (var (_, (cb, suppKeys)) in Snap(_keyPressListeners))
        {
            var captured = keyName;
            Dispatch(() => cb(captured));
            if (suppKeys.Contains(code))
                suppress = true;
        }

        if (suppress)
            e.SuppressEvent = true;
    }

    private void OnKeyReleased(object? sender, KeyboardHookEventArgs e)
    {
        var code = e.Data.KeyCode;
        var keyName = KeyName(code);
        bool suppress = false;

        lock (_lock)
            _pressedKeys.Remove(code);

        foreach (var (_, (cb, suppKeys)) in Snap(_keyReleaseListeners))
        {
            var captured = keyName;
            Dispatch(() => cb(captured));
            if (suppKeys.Contains(code))
                suppress = true;
        }

        if (suppress)
            e.SuppressEvent = true;
    }

    private void OnMouseMoved(object? sender, MouseHookEventArgs e)
    {
        int x = e.Data.X,
            y = e.Data.Y;
        foreach (var (_, cb) in Snap(_mouseMoveListeners))
            Dispatch(() => cb(x, y));
    }

    private void OnMousePressed(object? sender, MouseHookEventArgs e)
    {
        int x = e.Data.X,
            y = e.Data.Y;
        var btn = ButtonName(e.Data.Button);
        foreach (var (_, cb) in Snap(_mouseClickListeners))
            Dispatch(() => cb(x, y, btn, true));
    }

    private void OnMouseReleased(object? sender, MouseHookEventArgs e)
    {
        int x = e.Data.X,
            y = e.Data.Y;
        var btn = ButtonName(e.Data.Button);
        foreach (var (_, cb) in Snap(_mouseClickListeners))
            Dispatch(() => cb(x, y, btn, false));
    }

    // ── Helpers ───────────────────────────────────────────────────────────

    private static HashSet<KeyCode> ParseCombo(string combo) =>
        new(
            combo
                .Split('+', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                .Select(ParseKey)
        );

    private static HashSet<KeyCode> ParseKeySet(IEnumerable<string>? keys) =>
        keys is null ? [] : new(keys.Select(ParseKey));

    private List<KeyValuePair<string, T>> Snap<T>(Dictionary<string, T> dict)
    {
        lock (_lock)
            return [.. dict];
    }

    private static void Dispatch(Action action) =>
        Dispatcher.UIThread.Post(action, DispatcherPriority.Input);

    private static string ButtonName(MouseButton b) =>
        b switch
        {
            MouseButton.Button1 => "left",
            MouseButton.Button2 => "right",
            MouseButton.Button3 => "middle",
            _ => b.ToString().ToLowerInvariant(),
        };
}
