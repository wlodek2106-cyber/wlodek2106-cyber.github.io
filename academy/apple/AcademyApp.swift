import SwiftUI

@main
struct AcademyApp: App {
    var body: some Scene {
        WindowGroup {
            AcademyHome()
        }
    }
}
struct AcademyHome: View {
    @Environment(\.openURL) private var openURL
    var body: some View {
        VStack(spacing: 24) {
            Text("Z").font(.system(size: 84, weight: .black)).foregroundStyle(.purple)
            Text("ZER0LIFE Academy").font(.largeTitle.bold())
            Text("AI Creator & Developer").foregroundStyle(.secondary)
            Button("Open learning dashboard") {
                if let url = URL(string: "https://zer0life-academy.onrender.com/dashboard") {
                    openURL(url)
                }
            }.buttonStyle(.borderedProminent).tint(.purple)
            Button("Clear widget data") {
                AcademyProgressStore.clear()
            }.buttonStyle(.bordered)
            Text("Account sign-in and automatic widget synchronization are not yet integrated.")
                .font(.caption).foregroundStyle(.secondary)
        }.padding(32).frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
