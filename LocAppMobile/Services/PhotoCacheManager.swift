import Foundation
import UIKit
import Combine

/// Manages persistent photo caching on the device
/// Photos are stored in the Documents directory and persist between app launches
class PhotoCacheManager: ObservableObject {
    static let shared = PhotoCacheManager()

    @Published var downloadProgress: Double = 0
    @Published var isDownloading = false

    private let fileManager = FileManager.default
    private var photosDirectory: URL {
        let documentsPath = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        return documentsPath.appendingPathComponent("PropertyPhotos", isDirectory: true)
    }

    private init() {
        createPhotosDirectoryIfNeeded()
    }

    // MARK: - Directory Management

    private func createPhotosDirectoryIfNeeded() {
        if !fileManager.fileExists(atPath: photosDirectory.path) {
            try? fileManager.createDirectory(at: photosDirectory, withIntermediateDirectories: true)
        }
    }

    private func propertyDirectory(for propertySlug: String) -> URL {
        return photosDirectory.appendingPathComponent(propertySlug, isDirectory: true)
    }

    private func photosSubdirectory(for propertySlug: String) -> URL {
        return propertyDirectory(for: propertySlug).appendingPathComponent("photos", isDirectory: true)
    }

    private func accessSubdirectory(for propertySlug: String) -> URL {
        return propertyDirectory(for: propertySlug).appendingPathComponent("access", isDirectory: true)
    }

    // MARK: - Download Photos

    /// Downloads all photos for a property after token validation
    @MainActor
    func downloadPhotosForProperty(reservationId: Int, propertySlug: String) async {
        isDownloading = true
        downloadProgress = 0

        do {
            // Get property data to get photo list
            let propertyData = try await APIService.shared.getPropertyData(reservationId: reservationId)

            // Create directories
            let photosDir = photosSubdirectory(for: propertySlug)
            let accessDir = accessSubdirectory(for: propertySlug)

            try? fileManager.createDirectory(at: photosDir, withIntermediateDirectories: true)
            try? fileManager.createDirectory(at: accessDir, withIntermediateDirectories: true)

            let totalPhotos = propertyData.photos.count + propertyData.accessPhotos.count
            var downloadedCount = 0

            // Download property photos
            for photo in propertyData.photos {
                if let url = APIService.photoURL(propertySlug: propertySlug, filename: photo.filename) {
                    await downloadPhoto(from: url, to: photosDir.appendingPathComponent(photo.filename))
                }
                downloadedCount += 1
                downloadProgress = Double(downloadedCount) / Double(max(totalPhotos, 1))
            }

            // Download access photos
            for photo in propertyData.accessPhotos {
                if let url = APIService.accessPhotoURL(propertySlug: propertySlug, filename: photo.filename) {
                    await downloadPhoto(from: url, to: accessDir.appendingPathComponent(photo.filename))
                }
                downloadedCount += 1
                downloadProgress = Double(downloadedCount) / Double(max(totalPhotos, 1))
            }

            print("✅ Downloaded \(downloadedCount) photos for \(propertySlug)")

        } catch {
            print("❌ Error downloading photos: \(error)")
        }

        isDownloading = false
        downloadProgress = 1.0
    }

    private func downloadPhoto(from url: URL, to localPath: URL) async {
        // Skip if already exists
        if fileManager.fileExists(atPath: localPath.path) {
            return
        }

        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            try data.write(to: localPath)
        } catch {
            print("❌ Failed to download \(url.lastPathComponent): \(error.localizedDescription)")
        }
    }

    // MARK: - Get Cached Photo

    /// Returns the local URL for a cached photo, or nil if not cached
    func getCachedPhotoURL(propertySlug: String, filename: String, isAccessPhoto: Bool = false) -> URL? {
        let directory = isAccessPhoto ? accessSubdirectory(for: propertySlug) : photosSubdirectory(for: propertySlug)
        let localPath = directory.appendingPathComponent(filename)

        if fileManager.fileExists(atPath: localPath.path) {
            return localPath
        }
        return nil
    }

    /// Loads a cached photo as UIImage
    func getCachedImage(propertySlug: String, filename: String, isAccessPhoto: Bool = false) -> UIImage? {
        guard let localURL = getCachedPhotoURL(propertySlug: propertySlug, filename: filename, isAccessPhoto: isAccessPhoto) else {
            return nil
        }
        return UIImage(contentsOfFile: localURL.path)
    }

    // MARK: - Delete Photos

    /// Deletes all cached photos for a property
    func deletePhotosForProperty(propertySlug: String) {
        let propertyDir = propertyDirectory(for: propertySlug)

        if fileManager.fileExists(atPath: propertyDir.path) {
            do {
                try fileManager.removeItem(at: propertyDir)
                print("🗑️ Deleted photos for \(propertySlug)")
            } catch {
                print("❌ Failed to delete photos for \(propertySlug): \(error)")
            }
        }
    }

    /// Deletes all cached photos (cleanup)
    func deleteAllPhotos() {
        if fileManager.fileExists(atPath: photosDirectory.path) {
            do {
                try fileManager.removeItem(at: photosDirectory)
                createPhotosDirectoryIfNeeded()
                print("🗑️ Deleted all cached photos")
            } catch {
                print("❌ Failed to delete all photos: \(error)")
            }
        }
    }

    // MARK: - Cache Info

    /// Returns the total size of cached photos in bytes
    func getCacheSize() -> Int64 {
        guard fileManager.fileExists(atPath: photosDirectory.path) else { return 0 }

        var totalSize: Int64 = 0

        if let enumerator = fileManager.enumerator(at: photosDirectory, includingPropertiesForKeys: [.fileSizeKey]) {
            for case let fileURL as URL in enumerator {
                if let fileSize = try? fileURL.resourceValues(forKeys: [.fileSizeKey]).fileSize {
                    totalSize += Int64(fileSize)
                }
            }
        }

        return totalSize
    }

    /// Returns a formatted string of the cache size
    func getFormattedCacheSize() -> String {
        let bytes = getCacheSize()
        let formatter = ByteCountFormatter()
        formatter.allowedUnits = [.useKB, .useMB, .useGB]
        formatter.countStyle = .file
        return formatter.string(fromByteCount: bytes)
    }
}
