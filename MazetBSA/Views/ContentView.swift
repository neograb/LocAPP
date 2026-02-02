import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            // Onglet Accueil
            AccueilView()
                .tabItem {
                    Image(systemName: "house.fill")
                    Text("Accueil")
                }
            
            // Onglet Infos Pratiques (à développer)
            InfosPratiquesView()
                .tabItem {
                    Image(systemName: "info.circle.fill")
                    Text("Infos")
                }
            
            // Onglet Activités (à développer)
            ActivitesView()
                .tabItem {
                    Image(systemName: "star.fill")
                    Text("Activités")
                }
            
            // Onglet Contact (à développer)
            ContactView()
                .tabItem {
                    Image(systemName: "envelope.fill")
                    Text("Contact")
                }
        }
        .tint(Color("AccentColor"))
    }
}

#Preview {
    ContentView()
}
