import SwiftUI

struct ActivitesView: View {
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 25) {
                    
                    // En-tête
                    VStack(spacing: 10) {
                        Text("Découvrez l'Ardèche 🌿")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        Text("Nos recommandations autour de Bourg-Saint-Andéol")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                    
                    // Catégories d'activités
                    VStack(spacing: 20) {
                        
                        // Sites incontournables
                        ActivitySection(
                            title: "Incontournables",
                            icon: "star.fill",
                            color: .yellow,
                            items: [
                                ActivityItem(
                                    name: "Gorges de l'Ardèche",
                                    description: "Route panoramique spectaculaire • 15 min",
                                    emoji: "🏞️"
                                ),
                                ActivityItem(
                                    name: "Pont d'Arc",
                                    description: "Arche naturelle monumentale • 20 min",
                                    emoji: "🌉"
                                ),
                                ActivityItem(
                                    name: "Grotte Chauvet 2",
                                    description: "Réplique de la grotte préhistorique • 25 min",
                                    emoji: "🦴"
                                ),
                                ActivityItem(
                                    name: "Ferme aux Crocodiles",
                                    description: "Pierrelatte - Plus grand vivarium d'Europe • 15 min",
                                    emoji: "🐊"
                                ),
                            ]
                        )
                        
                        // Baignade & Activités nautiques
                        ActivitySection(
                            title: "Baignade & Kayak",
                            icon: "water.waves",
                            color: .blue,
                            items: [
                                ActivityItem(
                                    name: "Descente des Gorges en canoë",
                                    description: "Mini (8km) ou Maxi (32km) • Vallon",
                                    emoji: "🛶"
                                ),
                                ActivityItem(
                                    name: "Plages de l'Ardèche",
                                    description: "Saint-Martin-d'Ardèche • 10 min",
                                    emoji: "🏖️"
                                ),
                                ActivityItem(
                                    name: "Baignade au Pont d'Arc",
                                    description: "Site naturel exceptionnel • 20 min",
                                    emoji: "🏊"
                                ),
                            ]
                        )
                        
                        // Villes & Villages
                        ActivitySection(
                            title: "Villes à visiter",
                            icon: "building.2.fill",
                            color: .purple,
                            items: [
                                ActivityItem(
                                    name: "Bourg-Saint-Andéol",
                                    description: "Patrimoine riche, église romane • Sur place",
                                    emoji: "🏛️"
                                ),
                                ActivityItem(
                                    name: "Montélimar",
                                    description: "Capitale du nougat • 25 min",
                                    emoji: "🍬"
                                ),
                                ActivityItem(
                                    name: "Orange",
                                    description: "Théâtre antique (UNESCO) • 40 min",
                                    emoji: "🏟️"
                                ),
                                ActivityItem(
                                    name: "Avignon",
                                    description: "Palais des Papes, pont • 50 min",
                                    emoji: "🏰"
                                ),
                                ActivityItem(
                                    name: "Vallon-Pont-d'Arc",
                                    description: "Village touristique animé • 25 min",
                                    emoji: "🏘️"
                                ),
                            ]
                        )
                        
                        // Nature & Randonnées
                        ActivitySection(
                            title: "Nature & Randonnées",
                            icon: "leaf.fill",
                            color: .green,
                            items: [
                                ActivityItem(
                                    name: "Belvédères des Gorges",
                                    description: "Points de vue spectaculaires",
                                    emoji: "👀"
                                ),
                                ActivityItem(
                                    name: "Mont Ventoux",
                                    description: "Géant de Provence visible depuis BSA • 1h",
                                    emoji: "🏔️"
                                ),
                                ActivityItem(
                                    name: "Bois de Païolive",
                                    description: "Forêt de rochers sculptés • 40 min",
                                    emoji: "🌳"
                                ),
                            ]
                        )
                        
                        // Marchés
                        ActivitySection(
                            title: "Marchés provençaux",
                            icon: "basket.fill",
                            color: .orange,
                            items: [
                                ActivityItem(
                                    name: "Marché de Bourg-Saint-Andéol",
                                    description: "Samedi matin • Centre-ville",
                                    emoji: "🧺"
                                ),
                                ActivityItem(
                                    name: "Marché de Saint-Martin",
                                    description: "Jeudi matin • 10 min",
                                    emoji: "🍅"
                                ),
                                ActivityItem(
                                    name: "Marché de Pierrelatte",
                                    description: "Mardi & Vendredi matin • 15 min",
                                    emoji: "🫒"
                                ),
                            ]
                        )
                        
                        // Restaurants
                        ActivitySection(
                            title: "Bonnes tables",
                            icon: "fork.knife",
                            color: .red,
                            items: [
                                ActivityItem(
                                    name: "Restaurants de BSA",
                                    description: "Cuisine locale ardéchoise",
                                    emoji: "🍽️"
                                ),
                                ActivityItem(
                                    name: "Guinguettes de l'Ardèche",
                                    description: "Ambiance estivale au bord de l'eau",
                                    emoji: "🎶"
                                ),
                                ActivityItem(
                                    name: "Caves & Domaines viticoles",
                                    description: "Dégustation de vins locaux",
                                    emoji: "🍷"
                                ),
                            ]
                        )
                        
                        // Spécialités locales
                        ActivitySection(
                            title: "Spécialités à goûter",
                            icon: "sparkles",
                            color: .pink,
                            items: [
                                ActivityItem(
                                    name: "Caillette ardéchoise",
                                    description: "Spécialité de viande et herbes",
                                    emoji: "🥩"
                                ),
                                ActivityItem(
                                    name: "Picodon AOP",
                                    description: "Fromage de chèvre local",
                                    emoji: "🧀"
                                ),
                                ActivityItem(
                                    name: "Nougat de Montélimar",
                                    description: "La douceur provençale",
                                    emoji: "🍯"
                                ),
                                ActivityItem(
                                    name: "Châtaignes d'Ardèche",
                                    description: "En saison (automne)",
                                    emoji: "🌰"
                                ),
                            ]
                        )
                    }
                    .padding(.horizontal)
                    
                    // Note de bas de page
                    VStack(spacing: 10) {
                        Image(systemName: "lightbulb.fill")
                            .font(.title2)
                            .foregroundColor(.yellow)
                        
                        Text("Conseil")
                            .font(.headline)
                        
                        Text("En été, privilégiez les visites tôt le matin ou en fin de journée pour éviter la chaleur et l'affluence !")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 15)
                            .fill(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.05), radius: 5, x: 0, y: 2)
                    )
                    .padding(.horizontal)
                    
                    Spacer(minLength: 30)
                }
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Activités")
        }
    }
}

// MARK: - Modèle pour les activités
struct ActivityItem: Identifiable {
    let id = UUID()
    let name: String
    let description: String
    let emoji: String
}

// MARK: - Section d'activités
struct ActivitySection: View {
    let title: String
    let icon: String
    let color: Color
    let items: [ActivityItem]
    
    @State private var isExpanded = true
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // En-tête de section (cliquable)
            Button {
                withAnimation(.easeInOut(duration: 0.3)) {
                    isExpanded.toggle()
                }
            } label: {
                HStack {
                    Image(systemName: icon)
                        .font(.title2)
                        .foregroundColor(color)
                    
                    Text(title)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Spacer()
                    
                    Image(systemName: "chevron.down")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .rotationEffect(.degrees(isExpanded ? 0 : -90))
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(.systemBackground))
                )
            }
            
            // Liste des items (affichée si expanded)
            if isExpanded {
                ForEach(items) { item in
                    HStack(spacing: 15) {
                        Text(item.emoji)
                            .font(.title2)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.name)
                                .font(.subheadline)
                                .fontWeight(.medium)
                            
                            Text(item.description)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.03), radius: 3, x: 0, y: 1)
                    )
                    .transition(.opacity.combined(with: .move(edge: .top)))
                }
            }
        }
    }
}

#Preview {
    ActivitesView()
}
