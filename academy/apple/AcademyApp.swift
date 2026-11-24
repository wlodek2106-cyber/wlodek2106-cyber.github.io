import SwiftUI
import Foundation

@main
struct AcademyApp: App {
    var body: some Scene { WindowGroup { AcademyHome() } }
}
private struct LoginResponse: Decodable { let token: String }
private struct LearningProgress: Decodable {
    struct Lesson: Decodable { let completed: Bool }
    let paid: Bool
    let lessons: [Lesson]
}
@MainActor
final class AcademySession: ObservableObject {
    @Published var signedIn = false
    @Published var status = ""
    @Published var busy = false
    private var token: String?
    private let base = URL(string: "https://zer0life-academy.onrender.com")!
    private func request(_ path: String, body: [String:String]? = nil) async throws -> Data {
        var req = URLRequest(url: base.appendingPathComponent(path))
        req.cachePolicy = .reloadIgnoringLocalCacheData
        if let token { req.setValue("Bearer " + token, forHTTPHeaderField: "Authorization") }
        if let body {
            req.httpMethod = "POST"
            req.setValue("application/json", forHTTPHeaderField: "Content-Type")
            req.httpBody = try JSONSerialization.data(withJSONObject: body)
        }
        let (data,response) = try await URLSession.shared.data(for: req)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }
        return data
    }
    func login(email: String, password: String) async {
        guard !busy else { return }
        busy = true
        defer { busy = false }
        AcademyProgressStore.clear()
        do {
            token = try JSONDecoder().decode(LoginResponse.self, from: await request("login", body: ["email":email,"password":password])).token
            signedIn = true
            try await sync()
        } catch {
            token = nil
            signedIn = false
            status = "Sign-in or synchronization failed. Please retry."
        }
    }
    private func sync() async throws {
        let p = try JSONDecoder().decode(LearningProgress.self, from: await request("progress"))
        if p.paid && [30,40,45].contains(p.lessons.count) {
            AcademyProgressStore.update(completed: p.lessons.filter { $0.completed }.count, total: p.lessons.count)
            status = "Widget progress synchronized."
        } else {
            AcademyProgressStore.clear()
            status = "No active paid course."
        }
    }
    func refresh() async {
        guard signedIn && !busy else { return }
        busy = true
        defer { busy = false }
        do { try await sync() } catch {
            AcademyProgressStore.clear()
            status = "Synchronization failed. Please sign in again if your session expired."
        }
    }
    func logout() async {
        guard !busy else { return }
        busy = true
        defer { busy = false }
        _ = try? await request("logout", body: [:])
        token = nil
        signedIn = false
        AcademyProgressStore.clear()
        status = "Signed out."
    }
}
struct AcademyHome: View {
    @StateObject private var session = AcademySession()
    @State private var email = ""
    @State private var password = ""
    @Environment(\.openURL) private var openURL
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                Text("Z").font(.system(size: 84, weight: .black)).foregroundStyle(.purple)
                Text("ZER0LIFE Academy").font(.largeTitle.bold())
                Text("AI Creator & Developer").foregroundStyle(.secondary)
                if !session.signedIn {
                    TextField("Email", text: $email).textFieldStyle(.roundedBorder)
                    SecureField("Password", text: $password).textFieldStyle(.roundedBorder)
                    Button("Sign in & sync widget") {
                        Task { await session.login(email: email, password: password); password = "" }
                    }.buttonStyle(.borderedProminent).disabled(session.busy || email.isEmpty || password.isEmpty)
                } else {
                    Button("Refresh widget") { Task { await session.refresh() } }.buttonStyle(.borderedProminent).disabled(session.busy)
                    Button("Sign out") { Task { await session.logout() } }.disabled(session.busy)
                }
                Button("Open learning dashboard") {
                    if let url = URL(string: "https://zer0life-academy.onrender.com/dashboard") { openURL(url) }
                }.buttonStyle(.bordered)
                Text(session.status).font(.caption).foregroundStyle(.secondary)
            }.padding(32).frame(maxWidth: 500)
        }.frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
