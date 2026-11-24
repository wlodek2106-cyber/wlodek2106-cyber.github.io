import SwiftUI
@main
struct WatchAcademy: App {
    var body: some Scene {
        WindowGroup {
            VStack(spacing: 8) {
                Text("ZER0LIFE").font(.headline).foregroundStyle(.purple)
                Image(systemName: "graduationcap").font(.title)
                Text("AI Creator Academy").font(.caption)
                Text("Continue your lessons on your phone.").font(.footnote).multilineTextAlignment(.center)
            }
        }
    }
}
