import SwiftUI
import WidgetKit

struct AcademyEntry: TimelineEntry {
    let date: Date
    let completed: Int?
    let total: Int?
}
struct AcademyProvider: TimelineProvider {
    func placeholder(in context: Context) -> AcademyEntry {
        AcademyEntry(date: Date(), completed: 18, total: 40)
    }
    func getSnapshot(in context: Context, completion: @escaping (AcademyEntry) -> Void) {
        completion(context.isPreview ? placeholder(in: context) : current())
    }
    private func current() -> AcademyEntry {
        let store = UserDefaults(suiteName: "group.com.zer0life.academy")
        let total = store?.integer(forKey: "totalLessons") ?? 0
        let completed = store?.integer(forKey: "completedLessons") ?? 0
        guard [30,40].contains(total), (0...total).contains(completed) else {
            return AcademyEntry(date: Date(), completed: nil, total: nil)
        }
        return AcademyEntry(date: Date(), completed: completed, total: total)
    }
    func getTimeline(in context: Context, completion: @escaping (Timeline<AcademyEntry>) -> Void) {
        completion(Timeline(entries: [current()], policy: .after(Date().addingTimeInterval(1800))))
    }
}
struct AcademyWidgetView: View {
    let entry: AcademyEntry
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("ZER0LIFE").font(.caption.bold()).foregroundStyle(.purple)
            if let n = entry.completed, let total = entry.total {
                Text("\(n * 100 / total)%").font(.largeTitle.bold())
                ProgressView(value: Double(n), total: Double(total)).tint(.purple)
                Text("\(n) / \(total)").font(.caption)
            } else {
                Text("Open Academy").font(.headline)
                Text("Sync learning progress").font(.caption)
            }
            Spacer(minLength: 0)
            Text("Continue learning").font(.caption.bold())
        }
        .privacySensitive()
        .containerBackground(for: .widget) { Color(red: 0.08, green: 0.07, blue: 0.14) }
        .foregroundStyle(.white)
        .widgetURL(URL(string: "https://zer0life-academy.onrender.com/dashboard"))
    }
}
struct AcademyProgressWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "AcademyProgress", provider: AcademyProvider()) { entry in
            AcademyWidgetView(entry: entry)
        }
        .configurationDisplayName("ZER0LIFE Academy")
        .description("View your learning progress.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
