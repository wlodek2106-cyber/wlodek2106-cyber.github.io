import Foundation
import WidgetKit

enum AcademyProgressStore {
    static let group = "group.com.zer0life.academy"
    static func update(completed: Int, total: Int) {
        guard [30, 40, 45].contains(total), (0...total).contains(completed),
              let defaults = UserDefaults(suiteName: group) else { return }
        defaults.set(total, forKey: "totalLessons")
        defaults.set(completed, forKey: "completedLessons")
        WidgetCenter.shared.reloadTimelines(ofKind: "AcademyProgress")
    }
    static func clear() {
        guard let defaults = UserDefaults(suiteName: group) else { return }
        defaults.removeObject(forKey: "totalLessons")
        defaults.removeObject(forKey: "completedLessons")
        WidgetCenter.shared.reloadTimelines(ofKind: "AcademyProgress")
    }
}
