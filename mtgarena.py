import sys
import mysql.connector as mysql
from sphinxapi import SphinxClient, SPH_MATCH_ANY
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QGridLayout, QGroupBox, QListWidget, QWidget, QHBoxLayout, QListWidgetItem, QErrorMessage
from PyQt6.QtCore import Qt


class MTGArena(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup basic window properties
        self.setWindowTitle("MTG Arena Helper")
        self.setGeometry(100, 100, 800, 600)

        # Widget to hold all elements
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Define layout for the central widget
        self.layout = QGridLayout(self.central_widget)

        # Create all UI components
        self.create_ui_components()

        # Connect to MySQL database
        try:
            self.db = mysql.connect(
                host="localhost",
                user="MTGUser",
                password="MTGArena23!",
                database="mtg_arena_helper"
            )
            if self.db.is_connected():
                db_Info = self.db.get_server_info()
                print("Connected to MySQL database... MySQL Server version on ", db_Info)

                # create cursor
                cursor = self.db.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS mtg_arena_helper")
                cursor.execute("USE mtg_arena_helper")
                cursor.execute("CREATE TABLE IF NOT EXISTS cards(id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), type VARCHAR(255), colors VARCHAR(255))")
                self.db.commit()
        except mysql.Error as e:
            print("Error while connecting to MySQL", e)
            QErrorMessage.qtHandler()
            QErrorMessage.showMessage(str(e))
            sys.exit(1)

        # Initialize Sphinx client
        self.sphinx = SphinxClient()
        self.sphinx.SetServer('localhost', 9312)
        self.sphinx.SetMatchMode(SPH_MATCH_ANY)

    def closeEvent(self, event):
        if self.db.is_connected():
            self.db.close()
            print("Database connection closed.")

    def create_ui_components(self):
        # Search Bar
        self.search_entry = QLineEdit()
        self.layout.addWidget(self.search_entry, 0, 0)

        # Search button
        self.search_button = QPushButton("Search")
        self.layout.addWidget(self.search_button, 0, 1)
        self.search_button.clicked.connect(self.do_search)

        # Card type dropdown
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["Creature", "Instant", "Sorcery", "Enchantment", "Artifact", "Planeswalker", "Land"])
        self.layout.addWidget(self.type_dropdown, 0, 2)

        # Color checkboxes
        self.color_checkboxes = {
            "White": QCheckBox("White"),
            "Blue": QCheckBox("Blue"),
            "Black": QCheckBox("Black"),
            "Red": QCheckBox("Red"),
            "Green": QCheckBox("Green"),
        }
        color_group_box = QGroupBox("Colors")
        color_group_layout = QVBoxLayout()
        color_group_box.setLayout(color_group_layout)
        for checkbox in self.color_checkboxes.values():
            color_group_layout.addWidget(checkbox)
        self.layout.addWidget(color_group_box, 0, 3)

z        # Areas (Battlefield, Graveyard, Exile, Sideboard, Hand, Deck)
        self.areas = {
            "Battlefield": QListWidget(),
            "Graveyard": QListWidget(),
            "Exile": QListWidget(),
            "Sideboard": QListWidget(),
            "Hand": QListWidget(),
            "Deck": QListWidget(),
        }
        for i, (area_name, list_widget) in enumerate(self.areas.items(), start=1):
            area_group_box = QGroupBox(area_name)
            area_group_layout = QVBoxLayout()
            area_group_box.setLayout(area_group_layout)
            area_group_layout.addWidget(list_widget)
            self.layout.addWidget(area_group_box, 1, i)

    def do_search(self):
        # Clear previous results
        for area in self.areas.values():
            area.clear()

        # Get search text
        search_text = self.search_entry.text()

        # Execute Sphinx search
        results = self.sphinx.Query(search_text, "cards")

        # Check for errors
        if not results:
            print("Query failed: %s." % self.sphinx.GetLastError())
            return

        # Display results
        if results['matches']:
            for match in results['matches']:
                # Get card details from database
                cursor = self.db.cursor()
                cursor.execute("SELECT name, type, colors FROM cards WHERE id=%s", (match['id'],))
                card = cursor.fetchone()

                # Add card to results area
                self.add_card_to_area("Results", card)

        else:
            print("No results found.")

    def add_card_to_area(self, area_name, card):
        # Create widgets
        item_widget = QWidget()
        layout = QHBoxLayout(item_widget)
        text_label = QLabel(card[0])  # Card name
        area_dropdown = QComboBox()
        area_dropdown.addItems(self.areas.keys())

        # Add widgets to layout
        layout.addWidget(text_label)
        layout.addWidget(area_dropdown)

        # Create QListWidgetItem and set its widget to item_widget
        item = QListWidgetItem()
        item.setSizeHint(item_widget.sizeHint())
        self.areas[area_name].addItem(item)
        self.areas[area_name].setItemWidget(item, item_widget)

        # Connect area_dropdown's currentIndexChanged signal to a function to move the card
        area_dropdown.currentIndexChanged.connect(lambda index: self.move_card(card, area_dropdown.itemText(index)))

    def move_card(self, card, new_area):
        # TODO: Implement card moving
        pass
    
class Card:
    def __init__(self, id, name, type, cost, colors, power, toughness, text):
        self.id = id  # unique identifier for each card
        self.name = name
        self.type = type
        self.cost = cost  # represented as a dictionary e.g., {'colorless': 1, 'green': 1} for a cost of 1G
        self.colors = colors  # list of colors e.g., ['green']
        self.power = power  # relevant for creatures
        self.toughness = toughness  # relevant for creatures
        self.text = text  # rules text on the card

    def is_creature(self):
        return 'creature' in self.type.lower()

    def is_instant_or_sorcery(self):
        return 'instant' in self.type.lower() or 'sorcery' in self.type.lower()

class Player:
    def __init__(self, deck):
        self.life_total = 20
        self.deck = deck
        self.hand = []
        self.battlefield = []
        self.graveyard = []
        self.exile = []

    def draw_card(self):
        if len(self.deck) > 0:
            self.hand.append(self.deck.pop(0))

    def play_card(self, card):
        if card in self.hand:
            self.hand.remove(card)
            self.battlefield.append(card)

class GameState:
    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.active_player = 0  # index of the active player in the players list

    def get_active_player(self):
        return self.players[self.active_player]

    def get_opponent(self):
        return self.players[1 - self.active_player]

    def next_turn(self):
        self.active_player = 1 - self.active_player
        self.get_active_player().draw_card()

    def play_card_from_hand(self, player, card):
        if card.cost <= player.mana_pool and card in player.hand:
            player.play_card(card)
            if card.is_creature():
                player.battlefield.append(card)
            elif card.is_instant_or_sorcery():
                # TODO: Implement effects of instants and sorceries
                pass
            player.mana_pool -= card.cost

# Create the application
app = QApplication(sys.argv)

# Create and show the application's main window
window = MTGArena()
window.show()

# Run the application's main loop
sys.exit(app.exec())
