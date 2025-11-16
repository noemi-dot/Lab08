from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        # TODO
        results = []   #lista che conterrà i risultati

        for imp in self._impianti:
            consumi = imp.get_consumi()
            if consumi is None:
                results.append((imp.nome, 0))
                continue
            consumi_mese = [c.kwh for c in consumi if int(c.data.split("-")[1]) == mese]  #filtra solo i consumi del mese selezionato
            media = sum(consumi_mese) / len(consumi_mese) if consumi_mese else 0
            results.append((imp.nome, round(media, 2)))

        return results

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # TODO
        # Se abbiamo superato il settimo giorno, controlliamo se il costo corrente è migliore del costo ottimo trovato finora. Se sì, aggiorniamo la sequenza
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

            #  loop sugli impianti per calcolare il costo parziale
        for imp in self._impianti:
            imp_id = imp.id
            costo_giorno = consumi_settimana[imp_id][giorno - 1]
            nuovo_costo = costo_corrente + costo_giorno

            # costo di spostamento se cambio impianto
            if ultimo_impianto is not None and ultimo_impianto != imp_id:
                nuovo_costo += 5
            # Se il costo parziale è già peggiore del costo ottimo trovato, non procediamo con la ricorsione
            if self.__costo_ottimo != -1 and nuovo_costo >= self.__costo_ottimo:
                continue

            sequenza_parziale.append(imp_id)

            #chiamata ricorsiva per il giorno successivo
            self.__ricorsione(sequenza_parziale, giorno + 1, imp_id, nuovo_costo, consumi_settimana)

            sequenza_parziale.pop()

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        # TODO
        results = {imp.id: [0.0] * 7 for imp in self._impianti}

        for imp in self._impianti:
            consumi = imp.get_consumi()
            if consumi is None:
                continue

            for c in consumi:
                if int(c.data.split("-")[1]) == mese and 1 <= int(c.data.split("-")[2]) <= 7:
                    results[imp.id][int(c.data.split("-")[2]) - 1] = c.kwh

        return results

