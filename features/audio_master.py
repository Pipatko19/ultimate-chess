from PySide6 import QtMultimedia as qtmm
from PySide6 import QtCore as qtc
from pathlib import Path
import random

DIRECTORY = Path("data/sound")

PLACE_EFFECTS = "place-{0}.wav"
CLOCK_TICK = "clock_tick.wav"
FANFARE = "fanfare.wav"
PROMOTION = "promotion.wav"

class AudioMaster(qtc.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
    
        self.place_effects = [self._effect(PLACE_EFFECTS.format(n), 0.8) for n in range(1, 8)]
        self.tick_effect = self._effect(CLOCK_TICK, 0.05)
        
        self.fanfare = self._effect(FANFARE, 0.5)
        
        self.promotion = self._effect(PROMOTION, 0.8)
        
    def _effect(self, path: str, volume: float) -> qtmm.QSoundEffect:
        filepath = DIRECTORY / path
        effect = qtmm.QSoundEffect(self)
        
        if not filepath.exists():
            print(f'[AudioMaster] Sound file not found: {filepath}')
        
        effect.setSource(qtc.QUrl.fromLocalFile(str(filepath)))
        effect.setVolume(volume)
        return effect
    
    @qtc.Slot()
    def play_place_effect(self):
        random.choice(self.place_effects).play()
    
    @qtc.Slot()
    def play_tick_effect(self):
        self.tick_effect.play()
        
    @qtc.Slot()
    def play_fanfare_effect(self):
        self.fanfare.play()
    
    @qtc.Slot()
    def play_promotion_effect(self):
        self.promotion.play()