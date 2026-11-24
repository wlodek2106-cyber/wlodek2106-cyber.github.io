using System.Windows;
using Microsoft.Web.WebView2.Core;
namespace Academy;
public partial class MainWindow : Window {
    private const string Host = "zer0life-academy.onrender.com";
    public MainWindow() { InitializeComponent(); Loaded += Start; }
    private async void Start(object sender, RoutedEventArgs e) {
        try {
            var folder = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"Zer0Life","Academy");
            await Browser.EnsureCoreWebView2Async(await CoreWebView2Environment.CreateAsync(userDataFolder:folder));
            var core = Browser.CoreWebView2;
            core.Settings.AreHostObjectsAllowed = false;
            core.Settings.IsWebMessageEnabled = false;
            core.NavigationStarting += (_, args) => {
                if (!Uri.TryCreate(args.Uri,UriKind.Absolute,out var uri) || uri.Scheme != "https" || uri.Host != Host || !uri.IsDefaultPort) args.Cancel = true;
            };
            core.NewWindowRequested += (_, args) => { args.Handled = true; };
            core.PermissionRequested += (_, args) => { args.State = CoreWebView2PermissionState.Deny; };
            core.Navigate("https://"+Host+"/dashboard");
        } catch { MessageBox.Show("Unable to start Academy. Check WebView2 Runtime and internet access."); }
    }
}