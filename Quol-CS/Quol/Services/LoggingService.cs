using System;
using System.IO;

namespace Quol.Services;

/// <summary>
/// Simple colored console + error-file logger.
/// Mirrors qlogging.py: colored stdout by level, errors written to error.log.
/// </summary>
public static class LoggingService
{
    private static StreamWriter? _errorWriter;

    public static void Initialize()
    {
        var logPath = Path.Combine(AppContext.BaseDirectory, "error.log");
        _errorWriter = new StreamWriter(logPath, append: true) { AutoFlush = true };
    }

    public static void Debug(string message) => Log("DEBUG", message, ConsoleColor.DarkCyan);

    public static void Info(string message) => Log("INFO", message, ConsoleColor.Cyan);

    public static void Warning(string message) => Log("WARN", message, ConsoleColor.Yellow);

    public static void Error(string message, Exception? ex = null)
    {
        Log("ERROR", message, ConsoleColor.Red);
        if (ex is not null)
        {
            var entry = $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] ERROR: {message}\n{ex}\n";
            _errorWriter?.Write(entry);
        }
    }

    public static void Shutdown() => _errorWriter?.Dispose();

    private static void Log(string level, string message, ConsoleColor color)
    {
        var orig = Console.ForegroundColor;
        Console.ForegroundColor = color;
        Console.WriteLine($"[{level}] {message}");
        Console.ForegroundColor = orig;
    }
}
