VERSION = "0.1.1"
CREATORS = ["@aykut", "@NicKoehler"]
BOT_NAME = "Deezer downloader"
WELCOME_MSG = (
	f"🎵 Benvenuto su {BOT_NAME} 🎵\n\n"
	"Tocca /aiuto per ricevere più informazioni."
)
INFO_MSG = (
	f"👤 Devs: {', '.join(CREATORS)}\n"

	f"ℹ Versione: {VERSION}"
)
STATS_MSG = (
	"Il bot è attivo da: **{}**\n"
	"Spazio totale disco: **{}**\n"
	"Spazio Utilizzato: **{}**\n"
	"Spazio Libero: **{}**"
)
HELP_MSG = (
	"Cerca una traccia/album/playlist o inviami direttamente il link di una traccia/album/playlist e la scaricherò per te 😊\n\n"
	"**Lista dei comandi:**\n"
	"/start - Ricevi il messaggio di benvenuto\n"
	"/aiuto - Ricevi questo messaggio\n"
	"/stop - Ferma il download di album/playlist\n"
	"/impostazioni - Cambia le tue preferenze\n"
	"/info - Ricevi alcune informazioni utili riguardanti il bot\n"
	"/stats - Ricevi le statistiche del bot\n"
)

DOWNLOAD_MSG = "Recupero i dati neccessari per il download..."
UPLOAD_MSG = "Carico..."
END_MSG = "Finito."
ALBUM_MSG = (
	"💽 Album: {}\n"
	"👤 Artista: {}\n"
	"📅 Data di rilascio: {}\n"
	"🎧 Tracce totali: {}"
)
TRACK_MSG = (
	"🎧 Traccia: {}\n"
	"👤 Artista: {}\n"
	"💽 Album: {}\n"
	"📅 Data di rilascio: {}"
)
PLAYLIST_MSG = (
	"🎵 Titolo: {}\n"
	"🎧 Tracce totali: {}"
)
CHOOSE = "Scegli cosa fare:"
SEARCH_ALBUM = "Cerca un album 💽"
SEARCH_TRACK = "Cerca una traccia 🎧"
SEARCH_PLAYLIST = "Cerca una playlist 🎵"
