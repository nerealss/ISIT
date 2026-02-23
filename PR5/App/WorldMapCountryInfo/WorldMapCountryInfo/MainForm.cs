using System;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using System.Windows.Forms;
using GMap.NET;
using GMap.NET.MapProviders;
using GMap.NET.WindowsForms;
using GMap.NET.WindowsForms.Markers;
using Newtonsoft.Json.Linq;

namespace WorldMapCountryInfo
{
    public partial class MainForm : Form
    {
        private GMapOverlay markersOverlay;

        public MainForm()
        {
            // 1. НАСТРОЙКА СЕТИ ДО инициализации компонентов
            ConfigureNetworkSettings();

            InitializeComponent();
            InitializeMap();
        }

        private void ConfigureNetworkSettings()
        {
            // Настройка прокси и безопасности
            WebRequest.DefaultWebProxy = null;
            ServicePointManager.Expect100Continue = true;
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12 | SecurityProtocolType.Tls11 | SecurityProtocolType.Tls;

            // Создание папки для кэша вручную
            string cachePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "MapCache");
            if (!Directory.Exists(cachePath))
                Directory.CreateDirectory(cachePath);

            // Альтернативный способ кэширования
            try
            {
                // Попробуйте эту настройку для GMap.NET
                // Если не работает, просто пропустите
                var type = typeof(GMaps);
                var cacheLocationProp = type.GetProperty("CacheLocation");
                if (cacheLocationProp != null)
                {
                    cacheLocationProp.SetValue(null, cachePath, null);
                }
            }
            catch
            {
                // Игнорируем ошибку, если свойство недоступно
            }
        }

        // 1. Инициализация карты
        private void InitializeMap()
        {
            try
            {
                // ПРОВЕРЯЕМ РАЗНЫХ ПРОВАЙДЕРОВ ПО ОЧЕРЕДИ
                GMapProvider[] providers =
                {
                    GMapProviders.ArcGIS_World_Topo_Map,
                    GMapProviders.ArcGIS_World_Street_Map,
                    GMapProviders.BingMap,
                    GMapProviders.GoogleMap,
                    GMapProviders.YandexMap,
                    GMapProviders.OpenStreetMap
                };

                bool mapLoaded = false;
                foreach (var provider in providers)
                {
                    try
                    {
                        gMapControl1.MapProvider = provider;
                        gMapControl1.MinZoom = 2;
                        gMapControl1.MaxZoom = 18;
                        gMapControl1.Zoom = 4;
                        mapLoaded = true;
                        break;
                    }
                    catch
                    {
                        continue;
                    }
                }

                if (!mapLoaded)
                {
                    MessageBox.Show("Не удалось загрузить карту. Проверьте подключение к интернету.");
                    return;
                }

                // Настройка начального вида
                gMapControl1.Position = new PointLatLng(55.75, 37.61); // Москва
                gMapControl1.DragButton = MouseButtons.Left;
                gMapControl1.ShowCenter = false;
                gMapControl1.CanDragMap = true;

                // Размещение маркеров (синие точки) для ключевых стран
                markersOverlay = new GMapOverlay("markers");
                gMapControl1.Overlays.Add(markersOverlay);

                // Координаты СТОЛИЦ стран, а не центров
                AddCountryMarker(55.75, 37.61, "Russia", "Москва");
                AddCountryMarker(40.41, -3.70, "Spain", "Мадрид");
                AddCountryMarker(41.89, 12.49, "Italy", "Рим");
                AddCountryMarker(48.85, 2.35, "France", "Париж");
                AddCountryMarker(52.52, 13.40, "Germany", "Берлин");
                AddCountryMarker(51.50, -0.12, "United Kingdom", "Лондон");
                AddCountryMarker(39.90, 116.40, "China", "Пекин");
                AddCountryMarker(35.68, 139.69, "Japan", "Токио");
                AddCountryMarker(38.90, -77.03, "United States", "Вашингтон");
                AddCountryMarker(45.42, -75.69, "Canada", "Оттава");
                AddCountryMarker(-35.28, 149.13, "Australia", "Канберра");

                // Подписка на клик по маркеру
                gMapControl1.OnMarkerClick += GMapControl1_OnMarkerClick;

                // Также подпишемся на клик по карте (вариант Б)
                gMapControl1.MouseClick += GMapControl1_MouseClick;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка инициализации карты: {ex.Message}");
            }
        }

        private void GMapControl1_MouseClick(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Right)
            {
                // Получаем координаты клика
                var point = gMapControl1.FromLocalToLatLng(e.X, e.Y);

                // Показываем координаты
                MessageBox.Show($"Координаты: {point.Lat:F4}, {point.Lng:F4}\nКликните по маркеру для информации о стране.");
            }
        }

        private void AddCountryMarker(double lat, double lng, string countryId, string capital)
        {
            GMarkerGoogle marker = new GMarkerGoogle(new PointLatLng(lat, lng), GMarkerGoogleType.blue_dot);
            marker.Tag = countryId; // Имя страны для API
            marker.ToolTipText = $"{capital} ({countryId})\nКликните для информации";
            markersOverlay.Markers.Add(marker);
        }

        // 2. Взаимодействие пользователя (Вариант А)
        private async void GMapControl1_OnMarkerClick(GMapMarker item, MouseEventArgs e)
        {
            if (item.Tag != null)
            {
                await LoadCountryDataAsync(item.Tag.ToString());
            }
        }

        // 3. Обработка данных (REST API и JSON)
        private async Task LoadCountryDataAsync(string countryId)
        {
            try
            {
                // Показываем индикатор загрузки
                lblCountryName.Text = "Загрузка...";
                lblCurrency.Text = "Загрузка...";
                lblPopulation.Text = "Загрузка...";
                picFlag.Image = null;
                panelInfo.Visible = true;

                using (HttpClient client = new HttpClient())
                {
                    // Установка таймаута
                    client.Timeout = TimeSpan.FromSeconds(15);

                    // Асинхронный запрос к внешнему API
                    string url = $"https://restcountries.com/v3.1/name/{countryId}?fullText=true";

                    // Используем WebClient как альтернативу для лучшей совместимости
                    string response;
                    try
                    {
                        response = await client.GetStringAsync(url);
                    }
                    catch
                    {
                        // Fallback на WebClient
                        using (WebClient webClient = new WebClient())
                        {
                            response = await webClient.DownloadStringTaskAsync(url);
                        }
                    }

                    // Парсинг JSON-ответа
                    JArray data = JArray.Parse(response);
                    var country = data[0];

                    // Локализация (перевод на русский)
                    string nameRu = country["translations"]?["rus"]?["common"]?.ToString()
                        ?? country["name"]["common"].ToString();

                    // Извлечение валюты
                    string currencyName = "Нет данных";
                    string currencySymbol = "";
                    var currencies = country["currencies"];
                    if (currencies != null && currencies.HasValues)
                    {
                        var currencyNode = currencies.Children().First().First;
                        currencyName = currencyNode["name"].ToString();
                        currencySymbol = currencyNode["symbol"]?.ToString() ?? "";
                    }

                    // Извлечение населения и флага
                    long population = (long)country["population"];
                    string flagUrl = country["flags"]["png"].ToString();

                    // 4. Отображение результатов на информационной панели
                    UpdateUI(nameRu, flagUrl, currencyName, currencySymbol, population, country);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка при загрузке данных о стране '{countryId}': {ex.Message}",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                panelInfo.Visible = false;
            }
        }

        private void UpdateUI(string name, string flagUrl, string currency, string currencySymbol,
                            long population, JToken country = null)
        {
            try
            {
                lblCountryName.Text = name; // Название страны

                // Валюта с символом
                if (!string.IsNullOrEmpty(currencySymbol))
                    lblCurrency.Text = $"Валюта: {currency} ({currencySymbol})";
                else
                    lblCurrency.Text = $"Валюта: {currency}";

                // Форматированный вывод численности населения
                lblPopulation.Text = $"Население: {FormatPopulation(population)}";

                // Асинхронная загрузка флага
                Task.Run(() => LoadFlagImage(flagUrl));

                // Дополнительная информация, если есть
                if (country != null)
                {
                    string capital = country["capital"]?[0]?.ToString() ?? "Нет данных";
                    string region = country["region"]?.ToString() ?? "Нет данных";
                    // Можно добавить дополнительные поля при необходимости
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка обновления UI: {ex.Message}");
            }
        }

        private void LoadFlagImage(string flagUrl)
        {
            try
            {
                using (WebClient client = new WebClient())
                {
                    byte[] data = client.DownloadData(flagUrl);
                    this.Invoke(new Action(() =>
                    {
                        try
                        {
                            using (var stream = new System.IO.MemoryStream(data))
                            {
                                // Очищаем старое изображение
                                if (picFlag.Image != null)
                                {
                                    picFlag.Image.Dispose();
                                }
                                picFlag.Image = Image.FromStream(stream);
                            }
                        }
                        catch (Exception ex)
                        {
                            picFlag.Image = null;
                            // Не показываем ошибку пользователю для изображений
                        }
                    }));
                }
            }
            catch
            {
                // Игнорируем ошибки загрузки флагов
            }
        }

        private string FormatPopulation(long population)
        {
            if (population >= 1_000_000_000)
                return $"{(population / 1_000_000_000.0):F2} млрд чел.";
            else if (population >= 1_000_000)
                return $"{(population / 1_000_000.0):F1} млн чел.";
            else if (population >= 1_000)
                return $"{(population / 1_000.0):F1} тыс чел.";
            else
                return $"{population} чел.";
        }

        private void btnClose_Click(object sender, EventArgs e)
        {
            panelInfo.Visible = false;
        }

        // Очистка ресурсов при закрытии формы
        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            if (picFlag.Image != null)
            {
                picFlag.Image.Dispose();
                picFlag.Image = null;
            }

            // Очищаем маркеры
            if (markersOverlay != null)
            {
                markersOverlay.Markers.Clear();
                markersOverlay = null;
            }

            base.OnFormClosing(e);
        }

        // Метод для обновления провайдера карты (если нужно переключиться)
        private void SetMapProvider(GMapProvider provider)
        {
            try
            {
                gMapControl1.MapProvider = provider;
                gMapControl1.Refresh();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Не удалось переключить карту: {ex.Message}");
            }
        }
    }
}