from shiny import App, render, ui, reactive
import math

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Parametri Antropometrici"),
        ui.input_numeric("altezza", "Altezza (cm)", value=170, min=100, max=250),
        ui.input_numeric("peso", "Peso (kg)", value=70, min=30, max=200),
        ui.input_numeric("eta", "Età (anni)", value=30, min=1, max=120),
        ui.input_radio_buttons(
            "genere",
            "Genere",
            choices={"M": "Maschio", "F": "Femmina"},
            selected="M"
        ),
        ui.input_select(
            "etnia",
            "Etnia",
            choices={
                "white": "White",
                "black": "Black",
                "mexican": "Mexican American",
                "other": "Other"
            },
            selected="white"
        ),
        ui.input_numeric("vita", "Circonferenza vita (cm)", value=None),
        ui.input_numeric("polpaccio", "Circonferenza polpaccio (cm)", value=None),
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Rapporto Vita/Altezza"),
            ui.output_text("waist_height_ratio")
        ),
        ui.card(
            ui.card_header("Body Roundness Index (BRI)"),
            ui.output_text("bri")
        ),
        ui.card(
            ui.card_header("Fat Mass Index (FMI)"),
            ui.output_text("fmi")
        ),
        ui.card(
            ui.card_header("Body Surface Area (BSA)"),
            ui.output_text("bsa")
        ),
        ui.card(
            ui.card_header("Appendicular Skeletal Muscle Mass (ASM)"),
            ui.output_text("asm")
        ),
        ui.card(
            ui.card_header("Appendicular Skeletal Muscle Index (ASMI)"),
            ui.output_text("asmi")
        ),
        ui.card(
            ui.card_header("Resting Energy Expenditure (REE)"),
            ui.output_text("ree")
        ),
        col_widths=[6, 6, 6, 6, 6, 6, 12]
    ),
    title="Calcolatore Biomarker Antropometrici"
)

def server(input, output, session):
    
    @reactive.calc
    def bmi():
        """Calcola BMI"""
        if input.altezza() and input.peso():
            h_m = input.altezza() / 100
            return input.peso() / (h_m ** 2)
        return None
    
    @render.text
    def waist_height_ratio():
        """Calcola rapporto vita/altezza"""
        if input.vita() and input.altezza():
            ratio = input.vita() / input.altezza()
            risk = "Rischio cardiometabolico ELEVATO" if ratio >= 0.5 else "Rischio cardiometabolico nella norma"
            return f"Rapporto: {ratio:.3f}\n{risk}"
        return "Dati insufficienti per il calcolo (necessari: vita, altezza)"
    
    @render.text
    def bri():
        """Calcola Body Roundness Index"""
        if input.vita() and input.altezza():
            wc = input.vita()
            h = input.altezza()
            
            # BRI = 364.2 - 365.5 * sqrt(1 - (WC/(π*H))^2)
            inner = 1 - ((wc / (math.pi * h)) ** 2)
            if inner >= 0:
                bri_value = 364.2 - 365.5 * math.sqrt(inner)
                
                # Valutazione
                if 3.41 <= bri_value <= 6.91:
                    status = "Nella norma"
                elif bri_value < 3.41:
                    status = "Molto basso"
                else:
                    status = "Molto alto"
                
                return f"BRI: {bri_value:.2f}\nStato: {status}"
            else:
                return "Errore nel calcolo (valore negativo sotto radice)"
        return "Dati insufficienti per il calcolo (necessari: vita, altezza)"
    
    @render.text
    def fmi():
        """Calcola Fat Mass Index"""
        bmi_value = bmi()
        if bmi_value and input.eta():
            if input.genere() == "M":
                # Maschi: FMI = 0.0138 × anni + 0.6771 × BMI - 11.87
                fmi_value = 0.0138 * input.eta() + 0.6771 * bmi_value - 11.87
            else:
                # Femmine: FMI = 0.0171 × anni + 0.7486 × BMI - 10.68
                fmi_value = 0.0171 * input.eta() + 0.7486 * bmi_value - 10.68
            
            return f"FMI: {fmi_value:.2f} kg/m²\nBMI: {bmi_value:.2f} kg/m²"
        return "Dati insufficienti per il calcolo (necessari: peso, altezza, età)"
    
    @render.text
    def bsa():
        """Calcola Body Surface Area"""
        if input.peso() and input.altezza():
            kg = input.peso()
            cm = input.altezza()
            
            if input.genere() == "M":
                # Maschi: BSA = 0.000579479 × kg^0.38 × cm^1.24
                bsa_value = 0.000579479 * (kg ** 0.38) * (cm ** 1.24)
            else:
                # Femmine: BSA = 0.000975482 × kg^0.46 × cm^1.08
                bsa_value = 0.000975482 * (kg ** 0.46) * (cm ** 1.08)
            
            return f"BSA: {bsa_value:.3f} m²"
        return "Dati insufficienti per il calcolo (necessari: peso, altezza)"
    
    @render.text
    def asm():
        """Calcola Appendicular Skeletal Muscle Mass"""
        if input.polpaccio() and input.eta():
            calf = input.polpaccio()
            anni = input.eta()
            
            # sex: femmine 0, maschi 1
            sex = 1 if input.genere() == "M" else 0
            
            # etnia: white 0, black 1, Mexican American -0.540, other -0.402
            etnia_map = {
                "white": 0,
                "black": 1,
                "mexican": -0.540,
                "other": -0.402
            }
            etnia_value = etnia_map.get(input.etnia(), 0)
            
            # ASM = -10.427 + (calf × 0.768) - (anni × 0.029) + (sex × 7.523) + (etnia)
            asm_value = -10.427 + (calf * 0.768) - (anni * 0.029) + (sex * 7.523) + etnia_value
            
            return f"ASM: {asm_value:.2f} kg"
        return "Dati insufficienti per il calcolo (necessari: circonferenza polpaccio, età)"
    
    @render.text
    def asmi():
        """Calcola Appendicular Skeletal Muscle Index"""
        if input.polpaccio() and input.eta() and input.altezza():
            calf = input.polpaccio()
            anni = input.eta()
            
            # Calcola ASM
            sex = 1 if input.genere() == "M" else 0
            etnia_map = {
                "white": 0,
                "black": 1,
                "mexican": -0.540,
                "other": -0.402
            }
            etnia_value = etnia_map.get(input.etnia(), 0)
            asm_value = -10.427 + (calf * 0.768) - (anni * 0.029) + (sex * 7.523) + etnia_value
            
            # Calcola ASMI: ASM / h^2 (h in metri)
            h_m = input.altezza() / 100
            asmi_value = asm_value / (h_m ** 2)
            
            # Valutazione: Ridotto se < 7 per uomini, < 5.5 per donne
            if input.genere() == "M":
                status = "Ridotto" if asmi_value < 7 else "Non ridotto"
            else:
                status = "Ridotto" if asmi_value < 5.5 else "Non ridotto"
            
            return f"ASMI: {asmi_value:.2f} kg/m²\nStato: {status}"
        return "Dati insufficienti per il calcolo (necessari: circonferenza polpaccio, età, altezza)"
    
    @render.text
    def ree():
        """Calcola Resting Energy Expenditure con formule Marra e Harris-Benedict"""
        if input.peso() and input.eta() and input.altezza():
            kg = input.peso()
            anni = input.eta()
            cm = input.altezza()
            
            # Formula di Marra (2021) per atleti
            # REE = 17.2 × kg - 5.95 × anni + 748
            ree_marra = 17.2 * kg - 5.95 * anni + 748
            
            # Equazioni di Harris-Benedict (revisionate)
            if input.genere() == "M":
                # Maschi: REE = 88.362 + (13.397 × kg) + (4.799 × cm) - (5.677 × anni)
                ree_hb = 88.362 + (13.397 * kg) + (4.799 * cm) - (5.677 * anni)
            else:
                # Femmine: REE = 447.593 + (9.247 × kg) + (3.098 × cm) - (4.330 × anni)
                ree_hb = 447.593 + (9.247 * kg) + (3.098 * cm) - (4.330 * anni)
            
            return f"REE (Marra 2021 - atleti): {ree_marra:.0f} kcal/day\nREE (Harris-Benedict): {ree_hb:.0f} kcal/day"
        return "Dati insufficienti per il calcolo (necessari: peso, età, altezza)"

app = App(app_ui, server)
