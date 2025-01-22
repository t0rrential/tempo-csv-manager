from dotenv import set_key
from pathlib import Path
from os import getenv

from src.Router import Router
from src.SelfBot import SelfBot

from qfluentwidgets import MessageBoxBase, SubtitleLabel, PasswordLineEdit, BodyLabel, LineEdit, InfoBar, InfoBarPosition
from PyQt6.QtCore import Qt

envPath = Path(".env")

HOME_ADDRESS = getenv('HOME_ADDRESS')
GOOGLE_MAPS_APIKEY = getenv("GOOGLE_MAPS_APIKEY")
DISCORD_TOKEN = getenv("DISCORD_TOKEN")

class SettingsBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # google maps api
        self.gmapLabel = SubtitleLabel('Google Maps API Token', self)
        self.gmapsToken = PasswordLineEdit(self)

        self.gmapsToken.setText(GOOGLE_MAPS_APIKEY)
        self.gmapsToken.setPlaceholderText('Enter your API Token here')
        
        # discord api
        self.discordLabel = SubtitleLabel('Discord API Token', self)
        self.discordToken = PasswordLineEdit(self)

        self.discordToken.setText(DISCORD_TOKEN)
        self.discordToken.setPlaceholderText('Enter your API Token here')
        
        # home address
        self.homeLabel = SubtitleLabel('Home Address', self)
        self.homeLineEdit = LineEdit(self)

        self.homeLineEdit.setText(HOME_ADDRESS)
        self.homeLineEdit.setPlaceholderText('Address, City, State, Zip Code')
        
        # info msg
        self.info = BodyLabel("Note that these will be stored on your computer in the \'.env\' file.\n\
They will only be used to communicate with Discord, Google Maps, and to calculate routes (respectively).")

        # add widget to view layout
        self.viewLayout.addWidget(self.gmapLabel)
        self.viewLayout.addWidget(self.gmapsToken)
        
        self.viewLayout.addWidget(self.discordLabel)
        self.viewLayout.addWidget(self.discordToken)
        
        self.viewLayout.addWidget(self.homeLabel)
        self.viewLayout.addWidget(self.homeLineEdit)
        
        self.viewLayout.addWidget(self.info)        
        self.widget.setMinimumWidth(350)

    def validate(self):
        """ Override to validate form data """
        isValid = True
        invalid = []
        
        gmToken = self.gmapsToken.text()
        dcToken = self.discordToken.text()
        addr = self.homeLineEdit.text()
        
        checkGmaps = Router.checkKey(gmToken)
        if not(checkGmaps):
            invalid.append("Google Maps API Token")
        
        checkBot = SelfBot()
        checkDiscord = checkBot.check(dcToken)
        if not(checkDiscord):
            invalid.append("Discord Token")
        
        if checkGmaps:
            checkAddress = Router.checkAddress(gmToken, addr)
            if not(checkAddress):
                invalid.append("Address")
        
        if len(invalid) > 0:
            isValid = False
            invalidText = ", ".join(invalid)
            InfoBar.warning(
                title='Invalid Inputs',
                content=f"The following inputs are invalid: {invalidText}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=5000,
                parent=self
            )
        else:
            set_key(dotenv_path=envPath, key_to_set="HOME_ADDRESS", value_to_set=addr)
            set_key(dotenv_path=envPath, key_to_set="GOOGLE_MAPS_APIKEY", value_to_set=gmToken)
            set_key(dotenv_path=envPath, key_to_set="DISCORD_TOKEN", value_to_set=dcToken)
            
        return isValid