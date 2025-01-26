import httpx

class Area:
    def __init__(self, country="Россия", region="", city=""):
        """Конструктор. Принимает название страны, региона и города.
        Аргумент по умолчанию - Россия.
        Автоматически вызывает функцию getAreaId(), которая находит id по имени страны,
        региону и городу."""
        
        self.__country_name = country if country != "" else "Россия"
        self.__region_name = region
        self.__city_name = city
        self.__area_id = 0
        self.getAreaId()

    def getAreaId(self):
        """Запрашивает на hh.ru json со странами, регионами и городами,
        находит id страны, региона или города, чтобы передать потом в поиск.
        Полученный id сохраняет в self.__area_id
        Запускается автоматически из конструктора"""
        
        request_endpoint = "https://api.hh.ru/areas/"
        request_head = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = httpx.get(request_endpoint, headers=request_head)
        
        if response.status_code == 200:
            data = response.json()
            # Ищем страну
            country_data = next((item for item in data if item["name"] == self.__country_name), None)
            if not country_data:
                raise Exception(f'Страна "{self.__country_name}" не найдена.')

            self.__area_id = country_data["id"]  # Предполагаем, что если ничего не найдено, то это id страны
            
            # Ищем регион
            if self.__region_name:
                region_data = next((region for region in country_data["areas"] if region["name"] == self.__region_name), None)
                if region_data:
                    self.__area_id = region_data["id"]  # Если найден регион, сохраняем его id
                    
                    # Ищем город в регионе
                    if self.__city_name:
                        city_data = next((city for city in region_data["areas"] if city["name"] == self.__city_name), None)
                        if city_data:
                            self.__area_id = city_data["id"]  # Если найден город, сохраняем его id
            
            # Если город не указан, ищем его среди всех регионов
            elif self.__city_name:
                for region in country_data["areas"]:
                    city_data = next((city for city in region["areas"] if city["name"] == self.__city_name), None)
                    if city_data:
                        self.__area_id = city_data["id"]  # Если найден город в любом регионе, сохраняем его id

        else:
            raise Exception(f'Ошибка при запросе к {request_endpoint}.\nКод ошибки: {response.status_code}\n{response.text}')

    @property
    def area_id(self):
        return self.__area_id