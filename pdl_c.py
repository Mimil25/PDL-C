#!/usr/bin/python3

import argparse

ENTETE_CPP = 'fichiers/entete.cpp'

class Compilateur:
    def __init__(self, fichier_source):
        self.source_pdl = ""
        self.source_cpp = ""
        with open(fichier_source, 'r') as fichier:
            self.source_pdl = fichier.read()
            fichier.close()
        with open(ENTETE_CPP, 'r') as fichier:
            self.source_cpp = fichier.read()
            fichier.close()
        
        self.saisir_compteur = 0

    def separations(source):
        SEPARATIONS = ""
        symboles = [""]
        contexte = None
        for caracter in source:
            if contexte == "commentaire" and caracter != '\n':
                continue
            if caracter == '/' and symboles[-1] == '/':
                symboles.pop()
                contexte = "commentaire"
                continue
            
            if contexte == "chaine" and caracter != '"':
                symboles[-1] += caracter
                continue
            if caracter == '"':
                if contexte == "chaine":
                    contexte = None
                    symboles[-1] += caracter
                    symboles.append('')
                elif contexte == "caractere":
                    symboles[-1] += caracter
                else :
                    contexte = "chaine"
                    symboles.append('')
                    symboles[-1] += caracter
                continue
            
            if contexte == "caractere" and caracter != '\'':
                symboles[-1] += caracter
                continue
            if caracter == '\'':
                if contexte == "caractere":
                    contexte = None
                    symboles[-1] += caracter
                    symboles.append('')
                elif contexte == "chaine":
                    symboles[-1] += caracter
                else :
                    contexte = "caractere"
                    symboles.append('')
                    symboles[-1] += caracter
                continue

            if caracter == '\n':
                symboles.append(';')
            if caracter.isspace():
                if contexte is None:
                    continue
                contexte = None
                symboles.append('')
                continue

            elif caracter.isalpha():
                if contexte is None:
                    contexte = "identifiant"
                    symboles.append('')
                if "nombre" in contexte:
                    contexte = "identifiant"
                    symboles.append('')
            elif caracter.isnumeric():
                if contexte is None:
                    contexte = "nombre"
                    symboles.append('')
            elif caracter == '.':
                if contexte == "nombre":
                    contexte == "nombre flotant"
                elif contexte != "idendifiant":
                    contexte = "identifiant"
                    symboles.append('')
            else :
                contexte = None
                symboles.append('')
                
            symboles[-1] += caracter

        symboles = [symbole for symbole in symboles if symbole]
        return symboles

    def transformer_afficher(symboles, i):
        fonction = symboles[i]
        symboles[i] = 'std::cout'
        symboles[i + 1] = '<<'
        profondeur = 1
        j = i
        while profondeur:
            j += 1
            if symboles[j] == '(':
                profondeur += 1
            elif symboles[j] == ')':
                profondeur -= 1
            elif symboles[j] == ',' and profondeur == 1:
                symboles[j] = '<<'

        if fonction == 'afficherln':
            symboles[j] = '<<std::endl'
            if symboles[j-1] == '<<':
                symboles[j-1] = ''
        else :
            symboles[j] = ''

    def transformer_dansLeCasDe(symboles, i): #TODO
        symboles[i] = 'switch'
        while symboles[i] != ')': i += 1
        i += 1
        symboles[i] = '{case'
        profondeur = 0
        while profondeur:
            i += 1
            if symboles[i] == '{':
                profondeur += 1
            elif symboles[i] == '}':
                profondeur -= 1
            elif profondeur == 1 and symboles[i] == ':':
                j = i
                while symboles[j] != ';' and symboles[j] != '{':j -= 1
                j += 1
                i += 1




    def transformer_saisir(self, symboles, i):
        self.saisir_compteur += 1
        
        # déterminer le type attendu en sortie
        type_sortie = symboles[i-2]
        j = i
        while i-j < 10:
            j -= 1
            if symboles[j].startswith('"'):
                type_sortie = 'std::String'
                break
            if symboles[j].startswith('_'):
                k = symboles.index(symboles[j])
                while symboles[k] != ';' and symboles[k] != '{': k -= 1
                k += 1
                if symboles[k] == 'const':
                    k += 1
                type_sortie = symboles[k]
                break
            try :
                int(symboles[k])
                type_sortie = 'int'
                break
            except:
                pass
            try :
                float(symboles[k])
                type_sortie = 'float'
                break
            except:
                pass

        ##

        nom_var = '__tmp_{0}_var_{1}'.format(type_sortie, self.saisir_compteur)

        symboles[i] = nom_var
        symboles[i+1] = ''
        symboles[i+2] = ''
        j = i
        while symboles[j] != ';' and symboles[j] != '{':j -= 1
        symboles.insert(j+1, '{0} {1}; std::cin >> {1};'.format(type_sortie, nom_var))

    def remplacer(self, symboles):
        substitution_pdl = {'Principale':'main',
                            '←':'=',
                            'reel':'double',
                            'entier':'int',
                            'booleen':'bool',
                            'caractere':'char',
                            'chaine':'std::String',
                            'constante':'const',
                            'retourner':'return'}
       
        ignore = {'case', 'default'}
        i = 0
        while i < len(symboles):
            if symboles[i] in ignore:
                pass

            elif symboles[i] in substitution_pdl:
                symboles[i] = substitution_pdl[symboles[i]]
            
            elif symboles[i].startswith('fin'):
                symboles[i] = '}'

            elif symboles[i] == 'action':
                symboles[i] = 'int'
                j = i
                while symboles[j] != ')': j += 1
                symboles.insert(j+1, '{')
            
            elif symboles[i] == 'fonction':
                symboles[i] = ''
                j = i
                while symboles[j] != ')': j += 1
                symboles.insert(j+1, '{')

            elif symboles[i] == 'structure':
                symboles[i] = 'struct'
                symboles.insert(i+2, '{')

            elif symboles[i] == 'si':
                symboles[i] = 'if'
                j = i
                while symboles[j] != ')': j += 1
                symboles[j+1] = '{'

            elif symboles[i] == 'sinon':
                symboles[i] = '}else'
                if symboles[i+1] != 'si':
                    symboles[i] = '}else{'

            elif symboles[i] == 'dansLeCasDe':
                Compilateur.transformer_dansLeCasDe(symboles, i)

            elif symboles[i] == 'tantQue':
                symboles[i] = 'while'
                j = i
                while symboles[j] != ')': j += 1
                if symboles[i-1] == '}':
                    symboles[j+1] = ';'
                else :
                    symboles[j+1] = '{'

            elif symboles[i] == 'faire':
                symboles[i] = 'do{'
                j = i
                while symboles[j] != 'tantQue': j += 1
                symboles.insert(j, '}')
            
            elif symboles[i] == 'pour':
                symboles[i] = 'for(int '
                symboles[i+2] = '='
                symboles[i+4] = ';{0}<'.format('_' + symboles[i+1])
                symboles[i+6] = ';'
                symboles[i+7] = '_' + symboles[i+1] + '+='
                symboles[i+9] = '){'

            elif symboles[i] == 'afficher' or symboles[i] == 'afficherln':
                Compilateur.transformer_afficher(symboles, i)
            
            elif symboles[i] == 'saisir':
                self.transformer_saisir(symboles, i)

            elif symboles[i].isidentifier() and not symboles[i].startswith('__'):
                symboles[i] = '_' + symboles[i]
            i += 1
        return i

    def joint(symboles):
        chaine = ""
        for symbole in symboles:
            if symbole.isidentifier():
                chaine += symbole + ' '
            else:
                chaine += symbole
        return chaine
    
    def compile(self):
        symboles = Compilateur.separations(self.source_pdl)
        print(symboles)
        self.remplacer(symboles)
        self.source_cpp += Compilateur.joint(symboles)
        self.source_cpp += '\n'

    def enregistrer(self, sortie):
        with open(sortie, 'w') as fichier:
            fichier.write(self.source_cpp)
            fichier.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transform PDL code into C++ code.')
    parser.add_argument('source')
    parser.add_argument('--out', default='program.cpp')
    args = parser.parse_args()
    
    compilateur = Compilateur(args.source)
    compilateur.compile()
    compilateur.enregistrer(args.out)
