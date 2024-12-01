import yfinance as yf
from telegram_bot import warn, send_message_to_telegram, channel_00, channel_04
import pandas as pd
import time

VOLUME_RATIO = 1.3

TIME_FRAME = "1d"
CANDLE_COUNT = 3

# 1. BIST 30, BIST 100 ve BIST 500 Sembollerini Tanımlayın
def get_bist_symbols():
    # BIST sembolleri
    bistSymbols = [
        "A1CAP.IS","ACSEL.IS","ADEL.IS","ADESE.IS","ADGYO.IS","AEFES.IS","AFYON.IS","AGESA.IS","AGHOL.IS","AGROT.IS",
        "AHGAZ.IS","AHSGY.IS","AKBNK.IS","AKCNS.IS","AKENR.IS","AKFGY.IS","AKFYE.IS","AKGRT.IS","AKSA.IS","AKSEN.IS",
        "AKSUE.IS","AKYHO.IS","ALARK.IS","ALBRK.IS","ALCAR.IS","ALCTL.IS","ALFAS.IS","ALKA.IS","ALKIM.IS","ALKLC.IS",
        "ALMAD.IS","ALTIN.IS","ALTNY.IS","ALVES.IS","ANELE.IS","ANGEN.IS","ANHYT.IS","ANSGR.IS","ARASE.IS","ARCLK.IS",
        "ARDYZ.IS","ARSAN.IS","ARTMS.IS","ARZUM.IS","ASELS.IS","ASTOR.IS","ASUZU.IS","ATAKP.IS","ATATP.IS","ATEKS.IS",
        "ATLAS.IS","ATSYH.IS","AVGYO.IS","AVHOL.IS","AVOD.IS","AVPGY.IS","AYDEM.IS","AYEN.IS","AYES.IS","AYGAZ.IS",
        "BAGFS.IS","BAHKM.IS","BAKAB.IS","BALAT.IS","BANVT.IS","BARMA.IS","BASCM.IS","BASGZ.IS","BAYRK.IS","BEGYO.IS",
        "BERA.IS","BEYAZ.IS","BFREN.IS","BIENY.IS","BIGCH.IS","BINHO.IS","BIOEN.IS","BJKAS.IS","BLCYT.IS","BMSCH.IS",
        "BMSTL.IS","BNTAS.IS","BOBET.IS","BORLS.IS","BORSK.IS","BOSSA.IS","BRISA.IS","BRKO.IS","BRKSN.IS","BRLSM.IS",
        "BRMEN.IS","BRSAN.IS","BRYAT.IS","BSOKE.IS","BTCIM.IS","BUCIM.IS","BURCE.IS","BURVA.IS","BVSAN.IS","BYDNR.IS",
        "CANTE.IS","CASA.IS","CATES.IS","CCOLA.IS","CELHA.IS","CEMAS.IS","CEMTS.IS","CEMZY.IS","CEOEM.IS","CIMSA.IS",
        "CMBTN.IS","CMENT.IS","CONSE.IS","COSMO.IS","CRDFA.IS","CUSAN.IS","CVKMD.IS","CWENE.IS","DAGHL.IS","DAGI.IS",
        "DAPGM.IS","DARDL.IS","DENGE.IS","DERHL.IS","DERIM.IS","DESA.IS","DEVA.IS","DGNMO.IS","DIRIT.IS","DITAS.IS",
        "DMRGD.IS","DMSAS.IS","DNISI.IS","DOBUR.IS","DOCO.IS","DOFER.IS","DOGUB.IS","DOHOL.IS","DOKTA.IS","DURDO.IS",
        "DURKN.IS","DYOBY.IS","DZGYO.IS","ECILC.IS","ECZYT.IS","EDATA.IS","EDIP.IS","EFORC.IS","EGEEN.IS","EGEPO.IS",
        "EGGUB.IS","EGPRO.IS","EGSER.IS","EKGYO.IS","EKIZ.IS","EKOS.IS","EKSUN.IS","ELITE.IS","EMKEL.IS","EMNIS.IS",
        "ENERY.IS","ENJSA.IS","ENKAI.IS","ENSRI.IS","ENTRA.IS","EPLAS.IS","ERBOS.IS","ERCB.IS","EREGL.IS","ERSU.IS",
        "ESCAR.IS","ESCOM.IS","ESEN.IS","ETYAT.IS","EUHOL.IS","EUKYO.IS","EUPWR.IS","EUREN.IS","EUYO.IS","FADE.IS",
        "FENER.IS","FLAP.IS","FMIZP.IS","FONET.IS","FORMT.IS","FORTE.IS","FRIGO.IS","FROTO.IS","FZLGY.IS","GARAN.IS",
        "GARFA.IS","GEDIK.IS","GEDZA.IS","GENIL.IS","GENTS.IS","GEREL.IS","GESAN.IS","GIPTA.IS","GLBMD.IS","GLRYH.IS",
        "GLYHO.IS","GOKNR.IS","GOLTS.IS","GOODY.IS","GOZDE.IS","GRNYO.IS","GRTHO.IS","GSDHO.IS","GSRAY.IS","GUBRF.IS",
        "GUNDG.IS","GWIND.IS","HALKB.IS","HATEK.IS","HATSN.IS","HDFGS.IS","HEDEF.IS","HEKTS.IS","HKTM.IS","HTTBT.IS",
        "HUBVC.IS","HUNER.IS","HURGZ.IS","ICBCT.IS","ICUGS.IS","IEYHO.IS","IHAAS.IS","IHEVA.IS","IHGZT.IS","IHLAS.IS",
        "IHLGM.IS","IHYAY.IS","IMASM.IS","INFO.IS","INTEK.IS","INVEO.IS","INVES.IS","IPEKE.IS","ISATR.IS","ISBIR.IS",
        "ISBTR.IS","ISCTR.IS","ISDMR.IS","ISFIN.IS","ISGSY.IS","ISGYO.IS","ISKPL.IS","ISKUR.IS","ISMEN.IS","ISSEN.IS",
        "IZENR.IS","IZFAS.IS","IZINV.IS","IZMDC.IS","JANTS.IS","KAPLM.IS","KAREL.IS","KARSN.IS","KARTN.IS","KARYE.IS",
        "KATMR.IS","KAYSE.IS","KBORU.IS","KCAER.IS","KCHOL.IS","KENT.IS","KERVN.IS","KERVT.IS","KFEIN.IS","KLKIM.IS",
        "KLMSN.IS","KLNMA.IS","KLRHO.IS","KLSER.IS","KLSYN.IS","KMPUR.IS","KNFRT.IS","KOCMT.IS","KONKA.IS","KONTR.IS",
        "KONYA.IS","KOPOL.IS","KORDS.IS","KOTON.IS","KOZAA.IS","KOZAL.IS","KRDMA.IS","KRDMB.IS","KRDMD.IS","KRONT.IS",
        "KRPLS.IS","KRSTL.IS","KRTEK.IS","KRVGD.IS","KTLEV.IS","KTSKR.IS","KUTPO.IS","KUVVA.IS","KZBGY.IS","KZGYO.IS",
        "LIDFA.IS","LILAK.IS","LINK.IS","LKMNH.IS","LMKDC.IS","LOGO.IS","LRSHO.IS","LUKSK.IS","LYDYE.IS","MACKO.IS",
        "MAGEN.IS","MAKIM.IS","MAKTK.IS","MANAS.IS","MARBL.IS","MARKA.IS","MAVI.IS","MEDTR.IS","MEGAP.IS","MEGMT.IS",
        "MEKAG.IS","MERCN.IS","MERKO.IS","METRO.IS","MHRGY.IS","MIATK.IS","MMCAS.IS","MNDRS.IS","MNDTR.IS","MOGAN.IS",
        "MPARK.IS","MRSHL.IS","MTRKS.IS","MTRYO.IS","MZHLD.IS","NATEN.IS","NETAS.IS","NIBAS.IS","NTGAZ.IS","NTHOL.IS",
        "NUHCM.IS","OBAMS.IS","OBASE.IS","ODAS.IS","ODINE.IS","OFSYM.IS","ONCSM.IS","ONRYT.IS","ORCAY.IS","ORGE.IS",
        "ORMA.IS","OSMEN.IS","OSTIM.IS","OTKAR.IS","OTTO.IS","OYAKC.IS","OYAYO.IS","OYLUM.IS","OYYAT.IS","OZATD.IS",
        "OZRDN.IS","OZSUB.IS","OZYSR.IS","PAGYO.IS","PAMEL.IS","PAPIL.IS","PARSN.IS","PATEK.IS","PCILT.IS","PEKGY.IS",
        "PENGD.IS","PETKM.IS","PETUN.IS","PINSU.IS","PKART.IS","PNLSN.IS","PNSUT.IS","POLHO.IS","POLTK.IS","PRDGS.IS",
        "PRKAB.IS","PRKME.IS","PRZMA.IS","PSGYO.IS","QNBFL.IS","QUAGR.IS","RALYH.IS","RAYSG.IS","REEDR.IS","RGYAS.IS",
        "RNPOL.IS","RODRG.IS","ROYAL.IS","RTALB.IS","RUBNS.IS","SAFKR.IS","SAHOL.IS","SAMAT.IS","SANEL.IS","SANFM.IS",
        "SARKY.IS","SASA.IS","SAYAS.IS","SDTTR.IS","SEGMN.IS","SEGYO.IS","SEKFK.IS","SEKUR.IS","SELEC.IS","SELGD.IS",
        "SELVA.IS","SEYKM.IS","SILVR.IS","SISE.IS","SKBNK.IS","SKTAS.IS","SKYLP.IS","SKYMD.IS","SMART.IS","SMRTG.IS",
        "SNGYO.IS","SNICA.IS","SNKRN.IS","SNPAM.IS","SODSN.IS","SOKE.IS","SONME.IS","SRVGY.IS","SUMAS.IS","SUNTK.IS",
        "SURGY.IS","SUWEN.IS","TABGD.IS","TARKM.IS","TATEN.IS","TATGD.IS","TBORG.IS","TCELL.IS","TCKRC.IS","TDGYO.IS",
        "TERA.IS","TEZOL.IS","TKFEN.IS","TMPOL.IS","TMSN.IS","TNZTP.IS","TOASO.IS","TRCAS.IS","TRILC.IS","TSKB.IS",
        "TSPOR.IS","TTKOM.IS","TTRAK.IS","TUCLK.IS","TUKAS.IS","TUPRS.IS","TURGG.IS","TURSG.IS","UFUK.IS","ULKER.IS",
        "ULUFA.IS","ULUSE.IS","ULUUN.IS","UMPAS.IS","UNLU.IS","USAK.IS","VAKBN.IS","VAKFN.IS","VAKKO.IS","VANGD.IS",
        "VBTYZ.IS","VERTU.IS","VERUS.IS","VESBE.IS","VESTL.IS","VKFYO.IS","VKING.IS","VRGYO.IS","YAPRK.IS","YATAS.IS",
        "YAYLA.IS","YBTAS.IS","YEOTK.IS","YESIL.IS","YGGYO.IS","YIGIT.IS","YKBNK.IS","YKSLN.IS","YONGA.IS","YUNSA.IS",
        "YYAPI.IS","YYLGD.IS","ZOREN.IS","ZRGYO.IS","ARENA.IS","AVTUR.IS","BIMAS.IS","BIZIM.IS","CRFSA.IS","DESPC.IS",
        "DGATE.IS","DOAS.IS","ETILR.IS","INDES.IS","INTEM.IS","PENTA.IS","MEPET.IS","MGROS.IS","PSDTC.IS","SANKO.IS",
        "SOKM.IS","TGSAS.IS","TKNSA.IS","KIMMR.IS","MOBTL.IS","GMTAS.IS","AZTEK.IS","INGRM.IS","EBEBK.IS","DCTTR.IS",
        "LYDHO.IS","GRSEL.IS","AYCES.IS","KSTUR.IS","MAALT.IS","MARTI.IS","MERIT.IS","METUR.IS","GZNMI.IS","PKENT.IS",
        "ZEDUR.IS","TUREX.IS","TEKTU.IS","ULAS.IS","CLEBI.IS","GSDDE.IS","LIDER.IS","PGSUS.IS","RYSAS.IS","TAVHL.IS",
        "THYAO.IS","TLMAN.IS","PLTUR.IS","PASEU.IS","HOROZ.IS","HRKET.IS","BINBN.IS","GLCVY.IS","BRKVY.IS"
    ]

    # Tüm sembolleri birleştir ve benzersiz semboller olarak döndür
    all_symbols = list(set(bistSymbols))  # Tekrarlardan kurtulmak için set kullanıyoruz
    print(f"Toplam {len(all_symbols)} BIST sembolü bulundu.")
    return all_symbols

# 2. Belirtilen Sembol İçin 1 Günlük Son 3 Mum Verisini Çek
def get_last_ohlcv(symbol):
    try:
        # Yahoo Finance üzerinden veri çek (1 günlük son 3 mum)
        data = yf.download(symbol, period="7d", interval=TIME_FRAME)[-3:]
        if data.empty:
            print(f"{symbol} için veri alınamadı.")
            return None
        # OHLCV verisini düzenle
        df = data[["Open", "High", "Low", "Close", "Volume"]].reset_index()
        df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
        return df
    except Exception as e:
        print(f"Veri alınırken hata oluştu: {symbol}, Hata: {e}")
        return None

# 3. Hacmi Artan ve Yüzde 30 Kuralını Sağlayan Çiftleri Kontrol Et
def is_volume_increasing_by_percent(df):
    if len(df) < 3:
        return False
    # Hacimlerin %40 artıp artmadığını kontrol et
    vol_1 = df["volume"].iloc[0]
    vol_2 = df["volume"].iloc[1]
    vol_3 = df["volume"].iloc[2]
    return (vol_2 > vol_1 * VOLUME_RATIO) and (vol_3 > vol_2 * VOLUME_RATIO)

# 4. Tüm BIST Sembollerini Tarayarak Şartı Sağlayanları Bul
def scan_bist_symbols_with_increasing_volume():
    symbols = get_bist_symbols()
    increasing_volume_symbols = []

    for symbol in symbols:
        df = get_last_ohlcv(symbol)
        if df is not None and is_volume_increasing_by_percent(df):
            last_volume = df["volume"].iloc[-1]
            last_close = df["close"].iloc[-1]
            volume_value = last_volume * last_close
            increasing_volume_symbols.append({"symbol": symbol, "volume_value": volume_value})
            print(f"Hacmi artan sembol bulundu: {symbol}, İşlem Hacmi: {volume_value:,.2f}")
        # Her istekten sonra bekle
        time.sleep(0.05)

    # İşlem hacmine göre sırala
    sorted_symbols = sorted(increasing_volume_symbols, key=lambda x: x["volume_value"], reverse=True)
    return sorted_symbols

# Çalıştırma
if __name__ == "__main__":
    print("BIST bazlı semboller taranıyor...")
    results = scan_bist_symbols_with_increasing_volume()

    # Sıralanmış sonuçları al ve satır başına bir sembol olacak şekilde formatla
    sorted_results = [f"{item['symbol']} (Hacim: {item['volume_value']:,.2f} TRY)" for item in results]
    formatted_message = "\n".join(sorted_results)
       
    # Telegram mesajı gönder
    debugMsg = f"***\nZaman Aralığı: {TIME_FRAME}\nMum Sayısı : {CANDLE_COUNT}\n***\n\n" + f"*** SONUÇ ***\n\n{formatted_message}\n"
    print(debugMsg)
    send_message_to_telegram(channel_00, debugMsg)
    send_message_to_telegram(channel_04, debugMsg)
