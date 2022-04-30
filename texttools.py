from cgitb import reset


def _clean_numbers(string):
    '''
    Метод очищает строку от числовых данных
    '''
    import re
    string = re.sub('\\|\\d+i', '', string)
    string = re.sub('\\|\\d+>', '', string)
    string = re.sub('\\[[\\d+\\.\\-−–\\s,]+\\]', '', string)
    string = re.sub('\\(\\d+\\)', '', string)
    string = re.sub('\\b\\d+(\\.\\d+)?%?', '', string)
    string = string.replace('(cid:)', '')
    string = re.sub("\\(\\s?\\)", "", string)
    string = re.sub("\\[\\s?\\]", "", string)
    return string


def _remove_greek(string):
    '''
    Метод удаляет из текста греческие буквы и математические символы
    '''
    import re
    string = re.sub("[ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩω⊗†↓→∞↑↓=↔]+", "", string)
    return string


def _cut_tail(text):
    '''
    Метод обрезает неинформативные части статей - благодарности, списки литературы
    '''
    tails = ['acknowledgements\n', 'references\n', 'bibliograpy\n', 
         'confilicts of interest\n', "acknowledges support", "are grateful to the funding",
         'acknowledgements.', 'acknowledgment –', 'we thank', 'is gratefully acknowledged', 'appendix a', 'references .',
         'research was supported by', 'acknowledges support by', 'we acknowledge funding', 'work is supported by',
         'was supported by the funding', 'is supported by the funding', ]
    mintail = None
    for tail in tails:
        tailstart = text.lower().rfind(tail)
        if tailstart > -1:
            if mintail is None:
                mintail = tailstart
            else:
                if tailstart > len(text) // 2:
                    mintail = min(tailstart, mintail)
    if mintail is not None and mintail > -1 and mintail > len(text) // 2:
        text = text[:mintail]
    return text


def clean_text(text):
    '''
    Общий метод очистки текста. Вызывает все другие методы и нормализует пробелы и переносы строк.
    '''
    text = _cut_tail(text)
    text = text.replace('\r\n\r\n', ' ').replace('\n\n', ' ')
    text = '\n'.join([line for line in text.split('\n') if len(line.replace(' ', '')) > 3])
    text = text.replace("ﬃ", "ffi").replace("ﬁ", "fi").replace("ﬂ", "fl").replace('ﬀ', 'ff')
    text = _clean_numbers(text)
    text = _remove_greek(text)
    text = text.replace("-\n", "")
    text = text.replace("\n", " ")
    return text


def detect_abbreviations(text):
    '''
    Метод находит стандартный способ введения аббревиатур и возвращает словарь с ними
    '''
    import re
    result = {}
    abbr = re.compile("\(([A-Z]{2,})\)")
    for match in abbr.finditer(text):
        short = match.group(1)
        length = len(short)
        regex = f'((\\w+[\\s\-]+){{{length}}})\({short}\)'
        res = re.findall(regex, text)
        if res:
            result[match.group(1)] = res[0][0].strip()
    return result


def expand_abbreviations(text, abbreviations):
    '''
    Метод для заданного словаря аббревиатур подменяет их в тексте на полные обозначения
    '''
    import re
    for key in abbreviations:
        text = re.sub(f"\\s{key}", " " + abbreviations[key], text)
    return text    

if __name__ == "__main__":

    text = """The photonic crystal fiber (PCF) with a bunch of air holes enclosing the silica core field has momentous and compelling
attributes when compared with the ordinary single-mode fibers. In this work, both the birefringence and dispersion
properties of a polarization-maintaining chalcogenide (ChG) photonic crystal fiber are numerically investigated by means
as a very good candidate for ultra-broadband high bit-rate transmission.
Supercontinuum generation is another important application of PCF. Supercontinuum generation is a generation of
coherent and broadband light. SC generation in PCFs has several applications in optical coherence tomography (OCT),
optical frequency metrology (OFM), pulse compression, and design of ultrafast femtosecond laser pulses.
Different characteristics of the proposed
PCF are analyzed using the finite element method
(FEM) with perfectly matched layer (PML) boundary conditions
[48].
Choosing a right computational numerical technique
for solving a problem is very important. If we choose a
wrong technique, it can end up in incorrect result or it
takes a very long time to compute the results. Transient
response and impulse field effects are more accurately
computed by using the finite difference time-domain
(FDTD) method. Finite element method (FEM)
"""
    print(detect_abbreviations(text))
    print(expand_abbreviations(text, detect_abbreviations(text)))
