import logging

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu

logging.basicConfig(level=logging.DEBUG)

default_medications = {
    1: {"name": "Cefixime", "dose_per_kg": 8, "concentration": 20, "interval": "Every 12 hours"},
    2: {"name": "Azithromycin", "dose_per_kg": 10, "concentration": 40, "interval": "Once daily"},
    3: {"name": "Prednisolone", "dose_per_kg": 1, "concentration": 3, "interval": "Once daily"},
    4: {"name": "Ibuprofen", "dose_per_kg": 10, "concentration": 20, "interval": "Every 6 hours"},
    5: {"name": "Paracetamol (100 mg/ml)", "dose_per_kg": 15, "concentration": 100, "interval": "Every 4-6 hours"},
    6: {"name": "Paracetamol (120 mg/ 5 ml)", "dose_per_kg": 15, "concentration": 6, "interval": "Every 4-6 hours"},
    7: {"name": "Amoxicillin (250 mg/ 5 ml)", "dose_per_kg": 20, "concentration": 50, "interval": "Every 8 hours"},
    8: {"name": "Chlorpheniramine", "dose_per_kg": 0.25, "concentration": 1, "interval": "Every 4-6 hours"}
    # Add other medications...
}


class MedicationDoseCalculatorApp(MDApp):
    dialog = None

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(self.get_kv())

    def get_kv(self):
        return '''
MDBoxLayout:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(20)

    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(90)

        MDTextField:
            id: search_input
            hint_text: "Search Medication"
            mode: "rectangle"
            size_hint_y: None
            height: dp(100)
            on_text: app.update_suggestions(self.text)

        MDLabel:
            id: result_label
            text: "Search Medication and enter weight "
            size_hint_y: None
            halign: "center"
            valign: "middle"
            theme_text_color: "Primary"
            height: self.texture_size[1]

    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)

        MDTextField:
            id: weight_input
            hint_text: "Weight (kg)"
            mode: "rectangle"
            input_filter: "float"
            size_hint_y: None
            height: dp(40)

        MDTextField:
            id: dose_input
            hint_text: "Dose (mg/kg)"
            mode: "rectangle"
            input_filter: "float"
            size_hint_y: None
            height: dp(40)

        MDTextField:
            id: concentration_input
            hint_text: "Concentration (mg/ml)"
            mode: "rectangle"
            input_filter: "float"
            size_hint_y: None
            height: dp(40)

    MDBoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(40)
        spacing: dp(10)

        MDRaisedButton:
            text: "Calculate"
            md_bg_color: app.theme_cls.primary_color
            on_release: app.calculate_dose()

        MDRaisedButton:
            text: "Clear"
            md_bg_color: app.theme_cls.primary_color
            on_release: app.clear_fields()

    MDBoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(40)
        padding: dp(10)
        spacing: dp(10)
        pos_hint: {'center_x': 0.5}

        MDRaisedButton:
            text: "About"
            md_bg_color: app.theme_cls.primary_color
            on_release: app.show_about_dialog()    
'''

    def update_suggestions(self, text):
        text = text.strip().lower()
        suggestions = [med for med in default_medications.values() if text in med['name'].lower()]
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": suggestion['name'],
                "height": dp(40),
                "on_release": lambda x=suggestion['name']: self.on_suggestion_select(x)
            } for suggestion in suggestions
        ]
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        if menu_items:
            self.menu = MDDropdownMenu(
                caller=self.root.ids.search_input,
                items=menu_items,
                width_mult=4,
                border_margin=dp(4),
                position="bottom",
                padding="8dp"
            )
            self.menu.open()

    def on_suggestion_select(self, text):
        self.root.ids.search_input.text = text
        self.menu.dismiss()
        self.update_medication_params(text)

    def update_medication_params(self, text):
        medication = next((med for med in default_medications.values() if med['name'] == text), None)
        if medication:
            self.root.ids.dose_input.text = str(medication['dose_per_kg'])
            self.root.ids.concentration_input.text = str(medication['concentration'])
            self.root.ids.result_label.text = "Dose calculation will appear here."

    def calculate_dose(self):
        try:
            weight_text = self.root.ids.weight_input.text
            dose_text = self.root.ids.dose_input.text
            concentration_text = self.root.ids.concentration_input.text

            if not weight_text or not dose_text or not concentration_text:
                raise ValueError("All fields must be filled.")

            weight = float(weight_text)
            dose_per_kg = float(dose_text)
            concentration = float(concentration_text)

            total_dose = weight * dose_per_kg
            volume_required = total_dose / concentration

            medication_name = self.root.ids.search_input.text
            medication_interval = next(
                (med['interval'] for med in default_medications.values() if med['name'] == medication_name), "")

            self.root.ids.result_label.text = f"Dose: {total_dose:.2f} mg = {volume_required:.2f} ml, {medication_interval}"
        except ValueError as e:
            logging.error(f"Error in calculation: {e}")
            self.show_dialog(f"Error: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            self.show_dialog("An unexpected error occurred. Please check your inputs and try again.")

    def show_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDRaisedButton(
                        text="CLOSE",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
        else:
            self.dialog.text = message
        self.dialog.open()

    def show_about_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Medication Dose Calculator\nVersion 1.0\n© 2024 Clementine",
                buttons=[
                    MDRaisedButton(
                        text="CLOSE",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
        self.dialog.open()

    def clear_fields(self):
        self.root.ids.weight_input.text = ""
        self.root.ids.dose_input.text = ""
        self.root.ids.concentration_input.text = ""
        self.root.ids.search_input.text = ""
        self.root.ids.result_label.text = "Dose calculation will appear here."


if __name__ == '__main__':
    MedicationDoseCalculatorApp().run()
