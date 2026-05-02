using Avalonia.Controls;
using Quol.Views.Controls;

namespace PluginExample;

public partial class TestWindowView : UserControl
{
    public TestWindowView()
    {
        InitializeComponent();
    }

    public void SetTitle(string title)
    {
        var shell = this.FindControl<QuolClosableWindowShell>("Shell");
        if (shell is not null)
            shell.WindowTitle = title;
    }

    public void SetMathResult(string text)
    {
        var label = this.FindControl<TextBlock>("MathResultLabel");
        if (label is not null)
            label.Text = text;
    }
}
