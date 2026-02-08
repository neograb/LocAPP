import Foundation

// MARK: - Property Data Model

struct PropertyData: Decodable {
    let property: PropertyInfo
    let general: GeneralInfo?
    let wifi: WiFiInfo?
    let address: AddressInfo?
    let parking: ParkingInfo?
    let access: AccessInfo?
    let contact: ContactInfo?
    let emergencies: [Emergency]
    let services: [NearbyService]
    let activityCategories: [ActivityCategory]
    let activities: [Activity]
    let photos: [Photo]
    let accessPhotos: [AccessPhoto]

    enum CodingKeys: String, CodingKey {
        case property, general, wifi, address, parking, access, contact
        case emergencies, services
        case activityCategories = "activity_categories"
        case activities, photos
        case accessPhotos = "access_photos"
    }
}

struct PropertyInfo: Decodable {
    let id: Int
    let name: String
    let slug: String
    let icon: String?
    let location: String?
    let region: String?
    let theme: String?
    let accentColor: String?

    enum CodingKeys: String, CodingKey {
        case id, name, slug, icon, location, region, theme
        case accentColor = "accent_color"
    }
}

struct GeneralInfo: Decodable {
    let propertyName: String?
    let welcomeTitle: String?
    let welcomeMessage: String?
    let welcomeDescription: String?
    let headerImage: String?

    enum CodingKeys: String, CodingKey {
        case propertyName = "property_name"
        case welcomeTitle = "welcome_title"
        case welcomeMessage = "welcome_message"
        case welcomeDescription = "welcome_description"
        case headerImage = "header_image"
    }
}

struct WiFiInfo: Decodable {
    let ssid: String?
    let password: String?
    let locationDescription: String?

    enum CodingKeys: String, CodingKey {
        case ssid, password
        case locationDescription = "location_description"
    }
}

struct AddressInfo: Decodable {
    let street: String?
    let postalCode: String?
    let city: String?
    let country: String?
    let description: String?
    let latitude: Double?
    let longitude: Double?

    enum CodingKeys: String, CodingKey {
        case street
        case postalCode = "postal_code"
        case city, country, description, latitude, longitude
    }

    var fullAddress: String {
        var parts: [String] = []
        if let street = street { parts.append(street) }
        if let postalCode = postalCode, let city = city {
            parts.append("\(postalCode) \(city)")
        }
        return parts.joined(separator: ", ")
    }
}

struct ParkingInfo: Decodable {
    let distance: String?
    let description: String?
    let isFree: Bool?
    let tips: String?

    enum CodingKeys: String, CodingKey {
        case distance, description
        case isFree = "is_free"
        case tips
    }
}

struct AccessInfo: Decodable {
    let checkInTime: String?
    let checkOutTime: String?
    let keyboxCode: String?
    let keyboxLocation: String?
    let accessInstructions: String?

    enum CodingKeys: String, CodingKey {
        case checkInTime = "check_in_time"
        case checkOutTime = "check_out_time"
        case keyboxCode = "keybox_code"
        case keyboxLocation = "keybox_location"
        case accessInstructions = "access_instructions"
    }
}

struct ContactInfo: Decodable {
    let hostName: String?
    let phone: String?
    let email: String?
    let whatsapp: String?
    let airbnbUrl: String?
    let description: String?
    let responseTime: String?
    let avatar: String?

    enum CodingKeys: String, CodingKey {
        case hostName = "host_name"
        case phone, email, whatsapp
        case airbnbUrl = "airbnb_url"
        case description
        case responseTime = "response_time"
        case avatar
    }
}

struct Emergency: Decodable, Identifiable {
    let id: Int
    let name: String
    let number: String
    let category: String?
    let displayOrder: Int?

    enum CodingKeys: String, CodingKey {
        case id, name, number, category
        case displayOrder = "display_order"
    }
}

struct NearbyService: Decodable, Identifiable {
    let id: Int
    let name: String
    let category: String
    let icon: String?
    let address: String?
    let phone: String?
    let description: String?
    let openingHours: String?
    let displayOrder: Int?

    enum CodingKeys: String, CodingKey {
        case id, name, category, icon, address, phone, description
        case openingHours = "opening_hours"
        case displayOrder = "display_order"
    }
}

struct ActivityCategory: Decodable, Identifiable {
    let id: Int
    let name: String
    let icon: String?
    let color: String?
    let displayOrder: Int?

    enum CodingKeys: String, CodingKey {
        case id, name, icon, color
        case displayOrder = "display_order"
    }
}

struct Activity: Decodable, Identifiable {
    let id: Int
    let name: String
    let category: String
    let description: String?
    let emoji: String?
    let distance: String?
    let displayOrder: Int?

    enum CodingKeys: String, CodingKey {
        case id, name, category, description, emoji, distance
        case displayOrder = "display_order"
    }
}

struct Photo: Decodable, Identifiable {
    let id: Int
    let filename: String
    let title: String?
    let description: String?
    let displayOrder: Int?

    enum CodingKeys: String, CodingKey {
        case id, filename, title, description
        case displayOrder = "display_order"
    }
}

struct AccessPhoto: Decodable, Identifiable {
    let id: Int
    let filename: String
    let title: String?
    let description: String?
    let displayOrder: Int?

    enum CodingKeys: String, CodingKey {
        case id, filename, title, description
        case displayOrder = "display_order"
    }
}
