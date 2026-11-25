using System.Reflection;
namespace SefaXTV.WindowsLab;
internal static class Program
{
    [STAThread] private static void Main() { ApplicationConfiguration.Initialize(); Application.Run(new MainForm()); }
    internal static byte[] Asset(string name) { using var s = Assembly.GetExecutingAssembly().GetManifestResourceStream("SefaXTV.Assets." + name) ?? throw new InvalidOperationException("Missing asset " + name); using var m = new MemoryStream(); s.CopyTo(m); return m.ToArray(); }
}
