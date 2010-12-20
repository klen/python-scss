from collections import defaultdict

from scss.grammar import STYLESHEET, VARIABLE_ASSIGMENT, VAR_STRING, CHARSET, SELECTOR_GROUP, TERM, DECLARATION, DECLARESET, EXTEND, INCLUDE, MIXIN, MIXIN_PARAM, RULESET, COMMENT, VARIABLE, DEC_NAME


class Node(object):
    def __init__(self, t, stylecheet=None):
        self.t = list(t)
        self.stylecheet = stylecheet

class AtRule(Node):
    def render(self):
        return ' '.join(self.t) + ';'

class Term(Node):
    def render(self, context=None):
        return ''.join(e.render(context) if hasattr(e, 'render') else e for e in self.t)

class DecName(Node):
    def render(self, context=None):
        return ''.join(e.parse(context) if hasattr(e, 'parse') else e for e in self.t)

class Variable(Node):
    value = Term(('0', 'px'))
    def __init__(self, t, stylecheet):
        super(Variable, self).__init__(t, stylecheet)
        self.name = t[1]
    def parse(self, context=None):
        if context and context.get(self.name):
            self.value = context.get(self.name)
        else:
            self.value = self.stylecheet.context.get(self.name) or self.value
        return self.value.t[0]

class VarString(Node):
    def render(self, context=None):
        var = self.t[0]
        math = ''.join(
                e.parse(context) if hasattr(e, 'parse') else e for e in self.t)
        try:
            result = str(eval(math))
            return ''.join((result, var.value.t[1]))
        except SyntaxError:
            return var.value.render()

class Extend(Node):
    def parse(self, target):
        name = self.t[0]
        rulesets = target.stylecheet.ruleset.get(name)
        if rulesets:
            for rul in rulesets:
                selgroup = SelectorGroup(
                    target.selectorgroup[0].t + rul.selectorgroup[0].t[1:])
                rul.selectorgroup.append(selgroup)

class SelectorGroup(Node):
    def render(self):
        return ' '.join(self.t)
    def parse(self, target):
        target.selectorgroup.append(self)

class MixinParam(Node):
    def parse(self, target):
        target.mixinparam.append(self)
        try:
            self.t[0].value = self.t[1]
        except IndexError:
            pass

class Declaration(object):
    def __init__(self, t, stylecheet=None):
        self.name = t[0]
        self.terms = t[1:]
        self.context = None
    def parse(self, target):
        target.declaration.append(self)
    def render(self):
        return ':'.join((self.name.render(self.context), ' '.join(
                t.render(self.context) if hasattr(t, 'render') else t for t in self.terms
            )))

class AbstractSet(object):
    def __init__(self, t, stylecheet=None):
        self.name = t[0]
        self.stylecheet = stylecheet
        self.selectorgroup = []
        self.declaration = []
        self.ruleset = []

        for e in t:
            if hasattr(e, 'parse'):
                e.parse(self)

class DeclareSet(AbstractSet):
    def __init__(self, t, stylecheet=None):
        super(DeclareSet, self).__init__(t, stylecheet)
        for d in self.declaration:
            d.name = '-'.join((self.name, d.name))
    def parse(self, target):
        target.declaration += self.declaration

class Mixin(AbstractSet):
    def __init__(self, t, stylecheet=None):
        self.mixinparam = []
        super(Mixin, self).__init__(t, stylecheet)
        stylecheet.mix[self.name] = self
    def __len__(self):
        return False

class RuleSet(AbstractSet):
    def __init__(self, t, stylecheet):
        super(RuleSet, self).__init__(t, stylecheet)
        ancor = self.name.t[0]
        stylecheet.ruleset[ancor].add(self)
    def parse(self, target):
        target.ruleset.append(self)
    def render(self, parent=None):
        out = ''
        if self.declaration:
            # Selectors
            out += self.render_selectors(parent=parent)
            # Declaration
            out += self.render_declaration()
        # Ruleset
        for r in self.ruleset:
            out += '\n' + r.render(parent=self)
        return out
    def render_selectors(self, parent=None):
        if parent:
            selgroup = []
            for ps in parent.selectorgroup:
                for cs in self.selectorgroup:
                    s = ' '.join(cs.t)
                    if '&' in s:
                        s = s.replace('&', ' '.join(ps.t))
                        selgroup.append(SelectorGroup(s.split()))
                        break
                    else:
                        selgroup.append(SelectorGroup(ps.t+cs.t))
            self.selectorgroup = selgroup
        return ', '.join([s.render() for s in self.selectorgroup])
    def render_declaration(self):
        nl = '\n '# if len(self.declaration) > 1 else ' '
        # Sorting declarations alhabeticle
        self.declaration.sort(key=lambda x: x.name.t[0])
        return ''.join((' {', nl, ';\n '.join(
            d.render() for d in self.declaration
        ), ' }\n'))

class Include(object):
    def __init__(self, t, stylecheet):
        self.name = t[0]
        self.params = t[1:]
        self.mixin = stylecheet.mix.get(self.name)
    def parse(self, target):
        if self.mixin is None:
            return
        context = dict(self.get_context())
        for d in self.mixin.declaration:
            d.context = context
            target.declaration.append(d)
        target.ruleset += self.mixin.ruleset
    def get_context(self):
        it = iter(self.params)
        for param in self.mixin.mixinparam:
            try:
                yield (param.t[0].name, next(it))
            except StopIteration:
                yield (param.t[0].name, param.t[0].value)

class Stylecheet(object):

    def __init__(self, context = None, mixin = None, ignore_comment=True):
        self.context = context or dict()
        self.ignore_comment = ignore_comment
        self.mix = mixin or dict()
        self.ruleset = defaultdict(set)
        self.t = None

        VARIABLE_ASSIGMENT.setParseAction(self.var_assigment)

        COMMENT.setParseAction(self.comment)
        VARIABLE.setParseAction(self.getType(Variable))
        VAR_STRING.setParseAction(self.getType(VarString))
        CHARSET.setParseAction(self.getType(AtRule))
        SELECTOR_GROUP.setParseAction(self.getType(SelectorGroup))
        TERM.setParseAction(self.getType(Term))
        DECLARESET.setParseAction(self.getType(DeclareSet))
        DEC_NAME.setParseAction(self.getType(DecName))
        DECLARATION.setParseAction(self.getType(Declaration))
        EXTEND.setParseAction(self.getType(Extend))
        MIXIN_PARAM.setParseAction(self.getType(MixinParam))
        INCLUDE.setParseAction(self.getType(Include))
        MIXIN.setParseAction(self.getType(Mixin))
        RULESET.setParseAction(self.getType(RuleSet))

    def parse(self, src):
        self.t = STYLESHEET.parseString(src)

    def render(self):
        return '\n'.join(e.render() if hasattr(e, 'render') else e for e in self.t if e)

    def getType(self, node):
        def wrap(s, l, t):
            return node(t, self)
        return wrap

    def var_assigment(self, s, l, t):
        name, value = t
        self.context[name] = value
        return False

    def comment(self, s, l, t):
        if self.ignore_comment:
            return False
        return t[0]

def parse( src, context=None ):
    parser = Stylecheet(context)
    parser.parse(src)
    return parser.render()
