import SwiftUI

struct HistoryView: View {
    @State private var history: [HistoryEntry] = []
    @State private var isLoading = false
    @State private var error: String?

    var body: some View {
        NavigationStack {
            ZStack {
                if isLoading && history.isEmpty {
                    ProgressView("Chargement...")
                } else if history.isEmpty {
                    EmptyHistoryView()
                } else {
                    List {
                        ForEach(history) { entry in
                            HistoryRow(entry: entry)
                        }
                        .onDelete(perform: deleteEntry)
                    }
                    .refreshable {
                        await loadHistory()
                    }
                }
            }
            .navigationTitle("Historique")
            .task {
                await loadHistory()
            }
        }
    }

    private func loadHistory() async {
        isLoading = true
        error = nil

        do {
            let response = try await APIService.shared.getHistory()
            history = response.history
        } catch let apiError as APIError {
            error = apiError.errorDescription
        } catch {
            self.error = "Erreur de chargement"
        }

        isLoading = false
    }

    private func deleteEntry(at offsets: IndexSet) {
        for index in offsets {
            let entry = history[index]
            Task {
                do {
                    try await APIService.shared.deleteHistoryEntry(entry.id)
                    history.remove(at: index)

                    // Delete cached photos for this property
                    if let slug = entry.propertySlug {
                        PhotoCacheManager.shared.deletePhotosForProperty(propertySlug: slug)
                    }
                } catch {
                    self.error = "Erreur lors de la suppression"
                }
            }
        }
    }
}

// MARK: - Empty History View

struct EmptyHistoryView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "clock.badge.checkmark")
                .font(.system(size: 60))
                .foregroundColor(.gray.opacity(0.5))

            VStack(spacing: 8) {
                Text("Aucun historique")
                    .font(.title3)
                    .fontWeight(.medium)

                Text("Vos anciennes réservations apparaîtront ici")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
        }
        .padding()
    }
}

// MARK: - History Row

struct HistoryRow: View {
    let entry: HistoryEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("🏠")
                    .font(.title2)

                VStack(alignment: .leading, spacing: 2) {
                    Text(entry.propertyName)
                        .font(.headline)

                    if let address = entry.propertyAddress, !address.isEmpty {
                        Text(address)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                Spacer()
            }

            HStack {
                if let from = entry.stayedFrom, let to = entry.stayedUntil {
                    Text("\(formatDate(from)) → \(formatDate(to))")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                if let url = entry.bookingUrl, !url.isEmpty {
                    Link(destination: URL(string: url)!) {
                        HStack(spacing: 4) {
                            Image(systemName: "link")
                            Text("Réservation")
                        }
                        .font(.caption)
                    }
                }
            }

            if let comment = entry.personalComment, !comment.isEmpty {
                Text(comment)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .italic()
                    .padding(.top, 4)
            }
        }
        .padding(.vertical, 5)
    }

    private func formatDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withFullDate, .withTime, .withColonSeparatorInTime]

        if let date = formatter.date(from: dateString) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateFormat = "dd/MM/yy"
            return displayFormatter.string(from: date)
        }
        return dateString.prefix(10).description
    }
}

#Preview {
    HistoryView()
}
