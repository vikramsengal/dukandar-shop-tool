import os

# Kivy imports
try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.filechooser import FileChooserIconView
    from kivy.uix.popup import Popup
    from kivy.core.window import Window
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    from kivy.properties import StringProperty, ListProperty
except ImportError:
    print("Error: Kivy install nahi hai. 'pip install kivy' run karein.")
    exit()

# Ab hum `myfile.py` se logic import kar sakte hain
try:
    from myfile import (
        parse_csv_statement, parse_pdf_statement, Path, log_error,
        build_party_ledger, money
    )
except ImportError as e:
    print(f"Error: `myfile.py` se logic import nahi ho paya: {e}")
    # Dummy functions taaki app crash na ho
    def parse_csv_statement(path): raise NotImplementedError("Logic not loaded")
    def parse_pdf_statement(path): raise NotImplementedError("Logic not loaded")
    def build_party_ledger(txns): return []
    def money(x): return f"Rs {x:.2f}"
    def Path(p): return p
    def log_error(e): print(f"LOGIC_ERROR: {e}")

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # 1. Title
        layout.add_widget(Label(text="Dukandar GST Tool", font_size=32, size_hint=(1, 0.1), color=(1, 1, 0, 1)))

        # 2. Status Label
        self.status_label = Label(text="Select a file (.csv) to analyze", size_hint=(1, 0.1))
        layout.add_widget(self.status_label)

        # 3. File Chooser (Android/Desktop par file select karne ke liye)
        # Note: Android par permissions (READ_EXTERNAL_STORAGE) ki zaroorat padti hai buildozer.spec me
        self.file_chooser = FileChooserIconView(path=os.getcwd(), filters=['*.csv', '*.pdf'], size_hint=(1, 0.6))
        layout.add_widget(self.file_chooser)

        # 4. Analyze Button
        self.analyze_btn = Button(text="Analyze Selected File", size_hint=(1, 0.15), background_color=(0, 0.8, 0, 1))
        self.analyze_btn.bind(on_press=self.analyze_file)
        layout.add_widget(self.analyze_btn)
        
        self.add_widget(layout)

    def analyze_file(self, instance):
        selection = self.file_chooser.selection
        if selection:
            file_path = selection[0]
            self.status_label.text = f"Processing: {os.path.basename(file_path)}"
            
            try:
                ext = Path(file_path).suffix.lower()
                transactions = []
                if ext == ".csv":
                    total_debit, total_credit, rows_count, _, transactions = parse_csv_statement(file_path)
                elif ext == ".pdf":
                    total_debit, total_credit, rows_count, _, transactions = parse_pdf_statement(file_path)
                else:
                    self.show_popup("Error", "Sirf CSV/PDF supported hai.")
                    return

                result_text = (
                    f"Analysis Complete!\n\n"
                    f"Transactions: {rows_count}\n"
                    f"Total Debit: ₹ {total_debit:,.2f}\n"
                    f"Total Credit: ₹ {total_credit:,.2f}"
                )
                
                party_ledger = build_party_ledger(transactions)

                result_screen = self.manager.get_screen('result')
                result_screen.summary_text = result_text
                result_screen.party_ledger_data = party_ledger
                self.manager.current = 'result'

                self.status_label.text = "Analysis complete."
            except Exception as e:
                log_error(e)
                self.status_label.text = "Error during analysis."
                self.show_popup("Error", f"Analysis failed:\n{e}")
        else:
            self.status_label.text = "Please select a file first!"
            self.show_popup("Error", "Koi file select nahi ki gayi.")

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        close_btn = Button(text="Close", size_hint=(1, 0.25))
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

class ResultScreen(Screen):
    summary_text = StringProperty('')
    party_ledger_data = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        back_btn = Button(text="< Back to Main", size_hint=(1, 0.08))
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.summary_label = Label(text=self.summary_text, size_hint=(1, 0.25), halign='left', valign='top')
        self.summary_label.bind(size=self.summary_label.setter('text_size'))
        layout.add_widget(self.summary_label)

        layout.add_widget(Label(text="Party Ledger", font_size=24, size_hint=(1, 0.1)))

        scroll_view = ScrollView(size_hint=(1, 0.57))
        self.ledger_grid = GridLayout(cols=4, size_hint_y=None, spacing=5)
        self.ledger_grid.bind(minimum_height=self.ledger_grid.setter('height'))
        
        self.ledger_grid.add_widget(Label(text="Party", bold=True))
        self.ledger_grid.add_widget(Label(text="Paid", bold=True))
        self.ledger_grid.add_widget(Label(text="Received", bold=True))
        self.ledger_grid.add_widget(Label(text="Outstanding", bold=True))
        
        scroll_view.add_widget(self.ledger_grid)
        layout.add_widget(scroll_view)

        self.add_widget(layout)

    def on_summary_text(self, instance, value):
        self.summary_label.text = value

    def on_party_ledger_data(self, instance, value):
        for child in list(self.ledger_grid.children)[:-4]:
             self.ledger_grid.remove_widget(child)
        
        for item in value:
            outstanding = item['outstanding']
            color = (1, 1, 1, 1)
            if outstanding > 0: color = (0.5, 1, 0.5, 1)
            elif outstanding < 0: color = (1, 0.5, 0.5, 1)

            self.ledger_grid.add_widget(Label(text=str(item['party'])))
            self.ledger_grid.add_widget(Label(text=money(item['debit'])))
            self.ledger_grid.add_widget(Label(text=money(item['credit'])))
            self.ledger_grid.add_widget(Label(text=money(outstanding), color=color))

    def go_back(self, instance):
        self.manager.current = 'main'

class DukandarKivyApp(App):
    def build(self):
        # App ka background color set karein (Greyish)
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ResultScreen(name='result'))
        return sm

if __name__ == "__main__":
    DukandarKivyApp().run()
