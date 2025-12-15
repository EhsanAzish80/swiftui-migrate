import SwiftUI

// Example of fragile patterns (not deprecated, but problematic)

struct FragileNavigationView: View {
    @State private var showDetail = false
    @State private var showSettings = false
    
    var body: some View {
        NavigationView {
            VStack {
                // FRAG001 & FRAG002: NavigationLink with isActive
                NavigationLink(destination: DetailView(), isActive: $showDetail) {
                    Text("Go to Detail")
                }
                
                NavigationLink(destination: SettingsView(), isActive: $showSettings) {
                    EmptyView()
                }
                
                Button("Show Detail") {
                    showDetail = true
                }
            }
        }
    }
}

struct DataLoadingListView: View {
    @State private var items: [String] = []
    
    var body: some View {
        List {
            ForEach(items, id: \.self) { item in
                Text(item)
                    // FRAG003: onAppear in List/ForEach
                    .onAppear {
                        loadData()
                    }
            }
        }
    }
    
    func loadData() {
        // Network request here
    }
}

struct GeometryScrollView: View {
    var body: some View {
        ScrollView {
            // FRAG004: GeometryReader in ScrollView
            GeometryReader { geometry in
                Color.blue
                    .frame(height: geometry.size.width * 0.5)
            }
        }
    }
}

// FRAG005: @ObservedObject in root/app-level view
@main
struct MyApp: App {
    @ObservedObject var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}

class AppState: ObservableObject {
    @Published var isLoggedIn = false
}

struct DetailView: View {
    var body: some View {
        Text("Detail")
    }
}

struct SettingsView: View {
    var body: some View {
        Text("Settings")
    }
}

struct ContentView: View {
    var body: some View {
        Text("Content")
    }
}
