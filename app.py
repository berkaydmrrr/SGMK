import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Excel dosyasını yükleyin
df = pd.read_excel('/Users/berkaydemir/Desktop/VAKBN.xlsx')
verim_df = pd.read_excel('/Users/berkaydemir/Desktop/VAKBN.xlsx', sheet_name='Verim Eğrisi')  # Doğru sayfa adını buraya girin
data_df = pd.read_excel('/Users/berkaydemir/Desktop/VAKBN.xlsx', sheet_name='Data')  # Spread için kullanılan sayfa

# Tarih sütununu datetime formatına çevirin
df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')

# Sol tarafta ISIN Kodu ve tarih aralığı için giriş alanları oluşturun
isin_code = st.sidebar.selectbox('ISIN Kodu Seçin', df.columns[1:])  # 1. sütundan itibaren sütunları seç
start_date = st.sidebar.date_input('Başlangıç Tarihi', df['Tarih'].min())
end_date = st.sidebar.date_input('Bitiş Tarihi', df['Tarih'].max())

# Tarih aralığına göre verileri filtreleyin
filtered_data = df[(df['Tarih'] >= pd.to_datetime(start_date)) & (df['Tarih'] <= pd.to_datetime(end_date))]

# Seçilen ISIN koduna göre verileri alın
result = filtered_data[['Tarih', isin_code]]

# Ana başlıklar için sekmeler oluşturun
tab1, tab2, tab3 = st.tabs(["Bono", "Verim Eğrisi", "Spread"])

# Bono Sekmesi
with tab1:
    st.header(" ")
    st.write(f"{isin_code} için {start_date} ile {end_date} arasındaki veriler")

    # Matplotlib kullanarak bir grafik oluştur
    plt.figure(figsize=(10, 5))
    plt.plot(result['Tarih'], result[isin_code], marker='o', color='red')

    # Tarih eksenini düzgün göstermek için ayarları yapalım
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()  # Tarihlerin üst üste binmesini engellemek için eğik yazdırma

    plt.title(f'{isin_code} Bileşik Getiri')
    plt.xlabel(' ')
    plt.ylabel('')
    plt.grid(False)  # Izgaraları kaldırma
    st.pyplot(plt)

    # Filtrelenen verileri tablo olarak göster
    st.write("Veriler:")
    st.dataframe(result)

# Verim Eğrisi Sekmesi
with tab2:
    st.header(" ")

    # Kullanıcının seçebileceği diğer zaman dilimleri
    additional_times = st.sidebar.multiselect(
        "Eklemek istediğiniz zaman dilimlerini seçin",
        ['90 Gün Önce', '180 Gün Önce', '360 Gün Önce'],
        default=[]
    )

    # Zaman dilimlerini yeniden adlandırma
    verim_df = verim_df.rename(columns={
        'T': 'Bugün',
        'T-30': '30 Gün Önce'
    })

    # Grafik oluşturma
    plt.figure(figsize=(10, 5))
    plt.plot(verim_df.iloc[:, 0], verim_df['Bugün'], marker='o', color='red', label='Bugün')
    plt.plot(verim_df.iloc[:, 0], verim_df['30 Gün Önce'], marker='o', color='blue', label='30 Gün Önce')

    # Seçilen ek zaman dilimlerini grafiğe ekleme
    colors = ['green', 'purple', 'orange']  # Diğer zaman dilimleri için renkler
    for i, time in enumerate(additional_times):
        if time in verim_df.columns:
            plt.plot(verim_df.iloc[:, 0], verim_df[time], marker='o', color=colors[i], label=time)

    for i in range(len(verim_df)):
        plt.text(verim_df.iloc[i, 0], verim_df['Bugün'][i], f"{verim_df['Bugün'][i]:.2f}", color="red", ha="center")
        plt.text(verim_df.iloc[i, 0], verim_df['30 Gün Önce'][i], f"{verim_df['30 Gün Önce'][i]:.2f}", color="blue", ha="center")

    plt.title('Verim Eğrisi')
    plt.xlabel('')
    plt.ylabel('')
    plt.xticks(rotation=90)  # ISIN kodlarını daha iyi göstermek için
    plt.legend()
    plt.grid(False)  # Izgaraları kaldırma
    st.pyplot(plt)

    # Verim Eğrisi tablosunu göster
    st.write("Verim Eğrisi:")
    st.dataframe(verim_df)

# Spread Sekmesi
with tab3:
    st.header(" ")

    # ISIN Kodlarını Seçmek İçin
    available_isins = list(data_df.columns)[1:]  # İlk sütun tarih olduğu için diğer sütunları alıyoruz
    isin1 = st.selectbox('1. ISIN Kodu Seçin', available_isins)
    isin2 = st.selectbox('2. ISIN Kodu Seçin', available_isins)

    # Seçilen ISIN kodlarının verilerini alın
    spread_data1 = data_df[['Tarih', isin1]]
    spread_data2 = data_df[['Tarih', isin2]]

    # Spread hesaplama
    spread_difference = spread_data1[isin1] - spread_data2[isin2]
    spread_average = spread_difference.mean()

    # İlk Grafik: Seçilen ISIN kodlarının verileri
    plt.figure(figsize=(10, 5))
    plt.plot(spread_data1['Tarih'], spread_data1[isin1], marker='o', color='red', label=isin1)
    plt.plot(spread_data2['Tarih'], spread_data2[isin2], marker='o', color='black', label=isin2)
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()
    plt.title('SPREAD')
    plt.xlabel(' ')
    plt.ylabel('')
    plt.legend()
    plt.grid(False)
    st.pyplot(plt)

    # İkinci Grafik: Spread ve Ortalaması
    plt.figure(figsize=(10, 5))
    plt.plot(spread_data1['Tarih'], spread_difference, marker='o', color='red', label=f'{isin1} - {isin2}')
    plt.axhline(y=spread_average, color='black', linestyle='--', label=f'Ortalama: {spread_average:.2f}')
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()
    plt.title('Spread ve Ortalaması')
    plt.xlabel('Tarih')
    plt.ylabel('Spread Değeri')
    plt.legend()
    plt.grid(False)
    st.pyplot(plt)