import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculateur de Temps de Transport")
        self.geometry("450x350")
        
        # Base de données locale pour les agents : { "Nom": "HHMM" }
        self.agents_db = {}
        
        # Création des onglets
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        
        self.onglet_principal = ttk.Frame(self.notebook)
        self.onglet_param = ttk.Frame(self.notebook)
        
        self.notebook.add(self.onglet_principal, text="Calcul Principal")
        self.notebook.add(self.onglet_param, text="Paramétrage")
        
        # Initialisation des onglets
        self.creer_onglet_param()
        self.creer_onglet_principal()

    # --- ONGLET PARAMÉTRAGE ---
    def creer_onglet_param(self):
        frame = ttk.LabelFrame(self.onglet_param, text="Ajouter un agent", padding=15)
        frame.pack(fill="x", padx=15, pady=15)
        
        ttk.Label(frame, text="Nom de l'agent :").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_nom = ttk.Entry(frame)
        self.entry_nom.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Durée transport (HHMM) :").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_duree = ttk.Entry(frame)
        self.entry_duree.grid(row=1, column=1, pady=5, padx=5)
        
        btn_ajouter = ttk.Button(frame, text="Ajouter / Mettre à jour", command=self.ajouter_agent)
        btn_ajouter.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Liste visuelle des agents enregistrés
        self.liste_agents_txt = tk.Text(self.onglet_param, height=6, state="disabled")
        self.liste_agents_txt.pack(fill="both", padx=15, pady=5, expand=True)

    def ajouter_agent(self):
        nom = self.entry_nom.get().strip()
        duree = self.entry_duree.get().strip()
        
        if not nom or not duree:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
            
        if len(duree) != 4 or not duree.isdigit():
            messagebox.showerror("Erreur", "Le format de la durée doit être HHMM (ex: 0130 pour 1h30).")
            return
            
        # Enregistrement
        self.agents_db[nom] = duree
        
        # Mise à jour des interfaces
        self.maj_liste_visuelle_param()
        self.combo_agents['values'] = list(self.agents_db.keys())
        
        # Reset des champs
        self.entry_nom.delete(0, tk.END)
        self.entry_duree.delete(0, tk.END)
        messagebox.showinfo("Succès", f"Agent {nom} ajouté avec succès !")

    def maj_liste_visuelle_param(self):
        self.liste_agents_txt.config(state="normal")
        self.liste_agents_txt.delete("1.0", tk.END)
        for nom, duree in self.agents_db.items():
            self.liste_agents_txt.insert(tk.END, f"• {nom} : {duree[:2]}h{duree[2:]}\n")
        self.liste_agents_txt.config(state="disabled")

    # --- ONGLET PRINCIPAL ---
    def creer_onglet_principal(self):
        frame = ttk.Frame(self.onglet_principal, padding=15)
        frame.pack(fill="both", expand=True)
        
        # 1. Choix de l'agent
        ttk.Label(frame, text="Choisir un agent :").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_agents = ttk.Combobox(frame, values=list(self.agents_db.keys()), state="readonly")
        self.combo_agents.grid(row=0, column=1, pady=5)
        
        # 2. Heure début
        ttk.Label(frame, text="Début de poste (HH:MM) :").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_debut = ttk.Entry(frame)
        self.entry_debut.grid(row=1, column=1, pady=5)
        self.entry_debut.insert(0, "08:00") # Exemple par défaut
        
        # 3. Heure fin
        ttk.Label(frame, text="Fin de poste (HH:MM) :").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_fin = ttk.Entry(frame)
        self.entry_fin.grid(row=2, column=1, pady=5)
        self.entry_fin.insert(0, "17:00") # Exemple par défaut
        
        # Bouton Calculer
        btn_calculer = ttk.Button(frame, text="Calculer", command=self.calculer_temps)
        btn_calculer.grid(row=3, column=0, columnspan=2, pady=15)
        
        # 4. Résultat
        ttk.Label(frame, text="Résultat total :", font=("Arial", 11, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        self.lbl_resultat = ttk.Label(frame, text="--:--", font=("Arial", 12, "bold"), foreground="blue")
        self.lbl_resultat.grid(row=4, column=1, sticky="w", pady=5)

    def calculer_temps(self):
        agent_selectionne = self.combo_agents.get()
        h_debut_str = self.entry_debut.get().strip()
        h_fin_str = self.entry_fin.get().strip()
        
        if not agent_selectionne:
            messagebox.showerror("Erreur", "Veuillez sélectionner un agent.")
            return
            
        try:
            # Conversion des heures de poste (format HH:MM ou HHMM)
            fmt_debut = "%H:%M" if ":" in h_debut_str else "%H%M"
            fmt_fin = "%H:%M" if ":" in h_fin_str else "%H%M"
            
            t_debut = datetime.strptime(h_debut_str, fmt_debut)
            t_fin = datetime.strptime(h_fin_str, fmt_fin)
            
            # Gestion du cas où le poste finit le lendemain (ex: de 22h à 06h)
            if t_fin < t_debut:
                t_fin += timedelta(days=1)
                
            # Calcul de la durée de travail
            duree_travail = t_fin - t_debut
            
            # Récupération et conversion de la durée de transport (HHMM)
            duree_transport_str = self.agents_db[agent_selectionne]
            heures_tr = int(duree_transport_str[:2])
            minutes_tr = int(duree_transport_str[2:])
            duree_transport = timedelta(hours=heures_tr, minutes=minutes_tr)
            
            # Calcul Final : Fin - Début + Transport
            total_delta = duree_travail + duree_transport
            
            # Formatage du résultat
            total_secondes = int(total_delta.total_seconds())
            heures_totales = total_secondes // 3600
            minutes_totales = (total_secondes % 3600) // 60
            
            self.lbl_resultat.config(text=f"{heures_totales:02d}h{minutes_totales:02d}")
            
        except ValueError:
            messagebox.showerror("Erreur", "Format d'heure incorrect. Utilisez HH:MM (ex: 08:30).")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
