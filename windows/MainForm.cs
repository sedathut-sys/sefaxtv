using System.Text.Json;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

namespace SefaXTV.WindowsLab;

internal sealed class MainForm : Form
{
    private readonly WebView2 browser = new() { Dock = DockStyle.Fill };
    private readonly ProbeGate gate = new();
    private readonly HashSet<CoreWebView2Frame> frames = new();
    private bool ready, foreground = true, documentStarted, documentLoaded;
    private string? assetRoot;
    private CoreWebView2 Core => browser.CoreWebView2;
    public MainForm()
    {
        Text = "SefaXTV 0.13 — Windows LAB"; Width = 1100; Height = 850;
        MinimumSize = new Size(380, 420); StartPosition = FormStartPosition.CenterScreen;
        Controls.Add(browser); Shown += async (_, _) => await InitializeAsync();
        // No Deactivate handler: switching focus does not stop playback.
        Resize += (_, _) => Lifecycle();
        FormClosing += (_, _) => { ready = false; foreground = false; gate.NewDocument(); };
        FormClosed += (_, _) => { browser.Dispose(); try { if (assetRoot != null) Directory.Delete(assetRoot, true); } catch (IOException) { } catch (UnauthorizedAccessException) { } };
    }
    private async Task InitializeAsync()
    {
        try
        {
            // Extract exactly the three trusted embedded files to a fresh per-process directory.
            assetRoot = Path.Combine(Path.GetTempPath(), "SefaXTV-LAB-013-" + Guid.NewGuid().ToString("N"));
            var assets = Path.Combine(assetRoot, "assets"); Directory.CreateDirectory(assets);
            foreach (var name in new[] { "index.html", "lab-player.html" }) File.WriteAllBytes(Path.Combine(assets, name), Program.Asset(name));
            var profile = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "SefaXTV", "WindowsLab013", "WebView2");
            await browser.EnsureCoreWebView2Async(await CoreWebView2Environment.CreateAsync(userDataFolder: profile));
            Core.Settings.IsWebMessageEnabled = true; Core.Settings.AreDevToolsEnabled = false;
            Core.Settings.AreDefaultContextMenusEnabled = false; Core.Settings.AreHostObjectsAllowed = false;
            Core.Settings.IsStatusBarEnabled = false; Core.Settings.IsGeneralAutofillEnabled = false; Core.Settings.IsPasswordAutosaveEnabled = false;
            Core.SetVirtualHostNameToFolderMapping("appassets.androidplatform.net", assetRoot, CoreWebView2HostResourceAccessKind.DenyCors);
            Core.AddWebResourceRequestedFilter("*", CoreWebView2WebResourceContext.All);
            Core.WebResourceRequested += (_, e) => {
                if (!ProbeGate.ResourceAllowed(e.Request.Uri, e.Request.Method)) e.Response = Core.Environment.CreateWebResourceResponse(new MemoryStream(), 403, "Forbidden", "Content-Type: text/plain");
            };
            Core.NavigationStarting += (_, e) => { if (e.Uri != ProbeGate.App) { e.Cancel = true; return; } gate.NewDocument(); documentStarted = true; documentLoaded = false; frames.Clear(); };
            Core.NavigationCompleted += (_, e) => { documentLoaded = e.IsSuccess && Core.Source == ProbeGate.App; if (!documentLoaded) gate.NewDocument(); else if (foreground && ready) Hello(); };
            Core.NewWindowRequested += (_, e) => e.Handled = true;
            Core.PermissionRequested += (_, e) => e.State = CoreWebView2PermissionState.Deny;
            Core.DownloadStarting += (_, e) => e.Cancel = true;
            Core.FrameCreated += (_, e) => Attach(e.Frame, true);
            Core.WebMessageReceived += (_, e) => MainMessage(e);
            Core.ProcessFailed += (_, _) => { ready = false; gate.NewDocument(); documentStarted = documentLoaded = false; frames.Clear(); Text = "SefaXTV — WebView2 durdu; yeniden aç"; };
            await Core.AddScriptToExecuteOnDocumentCreatedAsync(System.Text.Encoding.UTF8.GetString(Program.Asset("observer.js")));
            ready = true; foreground = WindowState != FormWindowState.Minimized; Core.Navigate(ProbeGate.App);
        }
        catch (Exception ex) { ready = false; gate.NewDocument(); MessageBox.Show(this, "WebView2 başlatılamadı: " + ex.Message, "SefaXTV LAB", MessageBoxButtons.OK, MessageBoxIcon.Error); Close(); }
    }
    private void Attach(CoreWebView2Frame frame, bool direct)
    {
        if (!frames.Add(frame)) return;
        bool used = false;
        frame.NavigationStarting += (_, e) => {
            // Re-navigation even to same URL invalidates a previous binding. No second binding on this frame.
            if (gate.IsBound(frame)) gate.InvalidateFrame(frame);
            if (e.Uri is "about:blank" or "about:srcdoc") return;
            if (!direct || used || !foreground || !documentStarted || !gate.Bind(frame, e.Uri)) { e.Cancel = true; return; }
            used = true;
        };
        frame.NavigationCompleted += (_, e) => { if (!e.IsSuccess) gate.InvalidateFrame(frame); };
        frame.Destroyed += (_, _) => { frames.Remove(frame); gate.InvalidateFrame(frame); };
        frame.FrameCreated += (_, e) => Attach(e.Frame, false);
        frame.WebMessageReceived += (_, e) => {
            if (!ready || !foreground || !documentStarted || Core.Source != ProbeGate.App || !direct || !frames.Contains(frame) || !gate.IsBound(frame)) return;
            try { string raw = e.TryGetWebMessageAsString(); if (raw.Length > 2048) return; using var d = JsonDocument.Parse(raw); if (gate.Proof(frame, e.Source, d.RootElement)) Core.PostWebMessageAsString(raw); }
            catch (Exception ex) when (ex is InvalidOperationException or ArgumentException or JsonException or System.Runtime.InteropServices.COMException) { }
        };
    }
    private void Send(object message) { if (ready && documentStarted && Core.Source == ProbeGate.App) Core.PostWebMessageAsString(JsonSerializer.Serialize(message)); }
    private void Hello() { if (!foreground) return; gate.SetReady(true); Send(new { protocol = ProbeGate.Protocol, type = "host:ready", fixture = ProbeGate.Fixture }); }
    private void MainMessage(CoreWebView2WebMessageReceivedEventArgs e)
    {
        if (!ready || !foreground || !documentStarted || e.Source != ProbeGate.App || Core.Source != ProbeGate.App) return;
        try
        {
            string raw = e.TryGetWebMessageAsString(); if (raw.Length > 4096) return;
            using var j = JsonDocument.Parse(raw); var d = j.RootElement;
            if (d.GetProperty("protocol").GetString() != ProbeGate.Protocol) return;
            switch (d.GetProperty("type").GetString())
            {
                case "host:hello": Hello(); break;
                case "probe:start":
                    long seq = d.GetProperty("seq").GetInt64(); string? token = d.GetProperty("token").GetString(), url = d.GetProperty("url").GetString();
                    if (gate.Start(seq, token, url)) Send(new { protocol = ProbeGate.Protocol, type = "probe:armed", seq, token, url }); break;
                case "probe:stop": gate.Stop(d.GetProperty("seq").GetInt64(), d.GetProperty("token").GetString()); break;
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or KeyNotFoundException or ArgumentException or FormatException or OverflowException or JsonException or System.Runtime.InteropServices.COMException) { }
    }
    private void Lifecycle()
    {
        if (!ready) return;
        bool next = WindowState != FormWindowState.Minimized;
        if (foreground == next) return;
        foreground = next; gate.SetReady(false);
        if (!foreground) Send(new { protocol = ProbeGate.Protocol, type = "host:suspended" });
        else if (documentLoaded) Hello();
    }
}
