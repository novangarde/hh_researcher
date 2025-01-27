from . import area_identifier

class Config:
    def __init__(self):
        """Конструктор конфигурации.
        Ничего не принимает. Ничего не возвращает.
        Настройте поля для более корректного поиска.
        Оставьте поле пустым, если не хотите, чтобы оно хоть как-то влияло на фильтрацию.
        Если оставить пустым страну поиска, страной по умолчанию будет Россия

        :param __experience: Опыт работы: без опыта, от 1 до 3 лет, от 3 до 6 лет и более 6 лет.
        :param __employment: Тип занятости: полная, частичная, проектная, волонтерство, стажировка.
        :param __schedule: График работы:  полный день, неполный, гибкий, удаленный, вахтовый.
        :param __country: Страна поиска (По умолчанию "Россия")
        :param __region: Регион поиска (Не обязательное поле). Москва и Санкт-Петербург вписываются в это поле, а не в город
        :param __city: Город поиска
        :param __area_id: Область поиска: если указаны страна, регион (не обязательно) и город, ищет по городу, если страна и регион - по региону, если только страна - по стране
        """
        
        self.__experience = "noExperience" # ['noExperience', 'between1And3', 'between3And6', 'moreThan6']
        self.__employment = "full" # ['full', 'part', 'project', 'volunteer', 'probation']
        self.__schedule = "remote" # ['fullDay', 'shift', 'flexible', 'remote', 'flyInFlyOut']
        self.__country = "Россия" # Страна, к примеру, "Россия"
        self.__region = "Москва" # Регион, к примеру, "Республика Башкортостан"
        self.__city = "" # Город, к примеру, "Стерлитамак"
        self.__area_id = 0 # Заполняется автоматически, на основании заполненных выше полей
        self.update_area_id()

    def update_area_id(self):
        try:
            area_id = area_identifier.Area(self.country, self.region, self.city)
        except:
            raise Exception (f"Не работает update_area_id")
        self.__area_id = area_id.area_id

    @property
    def experience(self):
        return self.__experience
    
    @property
    def employment(self):
        return self.__employment
    
    @property
    def schedule(self):
        return self.__schedule
    
    @property
    def country(self):
        return self.__country
    
    @property
    def region(self):
        return self.__region
    
    @property
    def city(self):
        return self.__city

    @property
    def area_id(self):
        return self.__area_id
