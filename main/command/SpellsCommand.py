
from comm import RegexStore
from misc_functions import magentaprint
from command.Command import SimpleCommand
from comm import Spells

class SpellsCommand(SimpleCommand):
    command = 'spells'

    def __init__(self, telnetHandler, character):
        self.telnetHandler = telnetHandler
        self.character = character
        # self.regex_list = [RegexStore.spells1[0], RegexStore.spells2[0], RegexStore.spells3[0], RegexStore.spells4[0]]
        # magentaprint(str(self.regex_cart))
        # magentaprint(str(self))
        self.regex_cart = [RegexStore.spells]
        self.init()

    def init(self):
        self.regex_checker = [False, False, False, False, False]
        self.spells = []

    def notify(self, regex, M_obj):
        # self.character.spells = ' '.join((M_obj.group('black'), M_obj.group('white'), M_obj.group('misc'), M_obj.group('buffs'))).lower().split()
        # # self.character.spells = (M_obj.group('black')).lower().split()
        # magentaprint("Spells.notify()")
        # magentaprint(M_obj.group(0))
        # magentaprint(M_obj.group(1))
        # # self.character.spells = (M_obj.group('black')).lower().split()
        # magentaprint(str(self.character.spells))
        # for r in self.regex_cart:
        #     if regex in r:
        #         self.regex_checker[self.regex_cart.index()]
        self.regex_checker[self.regex_cart[0].index(regex)] = True

        # magentaprint("Groups: " + str(M_obj.groups()), True)
        groups = list(M_obj.groups())
        while None in groups:
            groups.remove(None)
        # spells = ' '.join(M_obj.groups()).lower().split()
        spells = ' '.join(groups).lower().split()
        while 'none' in spells:
            spells.remove('none')
        while '|' in spells:
            magentaprint(str(spells))
            spells.remove('|')
        # magentaprint('Spells...: ' + str(spells))

        # if 'level' in spells:
        #     try:
        #         # spells.remove('level')
        #         # spells.remove('earth')
        #         # spells.remove('wind')
        #         # spells.remove('water')
        #         # spells.remove('fire')
        #         # spells.remove('astral')
        #         # spells.remove('1')
        #         # spells.remove('2')
        #         # spells.remove('3')
        #         # spells.remove('4')
        #         # spells.remove('5')
        #     except:
        #         magentaprint("Spells.notify() error removing the extraneous.")
        # for long_spellname in self.spells:
        #     if any(long_spellname.startswith(short_spellname) for short_spellname in dir(Spells) if not s.startswith('__')):
        #         self.spells.extend(spells)
        #     else:
        #         magentaprint("Spells error!  : %s, %s" % long_spellname, short_spellname)

        for i in range(0, len(spells)):
            # if spells[i].startswith(s) for s in dir(Spells) if not s.startswith('__'): 
            #     spells[i] = s
            # for short_spellname in dir(Spells) if not s.startswith('__'):
            for spell_variable_name in dir(Spells):
                # magentaprint(spell_variable_name + spells[i], False)
                if not spell_variable_name.startswith('_') and spells[i].startswith(getattr(Spells, spell_variable_name)):
                    # magentaprint("Extending: " + str(getattr(Spells, spell_variable_name)), False)
                    # spells[i] = spell_variable_name
                    self.spells.append(getattr(Spells, spell_variable_name))
                    # self.spells.append(spell_variable_name)

        # magentaprint('---', False)
        # magentaprint(str(spells), False)
        # magentaprint(str(dir(Spells)), False)
        # magentaprint('---', False)
        # magentaprint(str(list(s for s in dir(Spells) if any(s2.startswith(s) for s2 in spells))), False)
        # spells.append("woohoo")
        # self.spells.extend(getattr(Spells, s) for s in dir(Spells) if not s.startswith('__') and any(s2.replace('-','').startswith(s) for s2 in spells))
        # self.character.spells.extend(s) for s in dir(Spells) if not s.startswith('__') and any(s2.startswith(s) for s2 in spells)
        # self.spells.extend(getattr(Spells, s) for s in dir(Spells) if not s.startswith('__') and any(s2.startswith(getattr(Spells,s)) for s2 in spells))
        # self.spells.extend(getattr(Spells, s) for s in dir(Spells) if any(s2.startswith(getattr(Spells,s)) for s2 in spells))  # getting dict variables out of dir(Spells)
        spellnames = (s for s in dir(Spells) if not s.startswith('_'))  # try a list
        # magentaprint('spells variable names: ' + str(list(spellnames)), False)
        # magentaprint('spells variable values: ' + str(getattr(Spells, s) for s in spellnames), False)
        # magentaprint('m_obj misc2: %s' % M_obj.group('misc2'), False)
        # magentaprint('m_obj groups: %s' % str(M_obj.groups()), False)

        # self.spells.extend(getattr(Spells, s) for s in spellnames if any(s2.startswith(getattr(Spells, s)) for s2 in spells)) 
        # self.spells.extend(getattr(Spells, s) for s in spellnames if any(s2.startswith(getattr(Spells, s)) for s2 in spells)) 

        # if all(self.regex_checker):
        if sum(self.regex_checker) >= 1:
            magentaprint("Spells: %s" % str(self.spells))
            self.character.spells = self.spells
            self.init()
            super().notify(regex, M_obj)

