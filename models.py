import datetime
import uuid
from uuid6 import uuid7
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./profiles.db"
engine = create_engine(DATABASE_URL,
                       connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

COUNTRY_MAP = {
    "NG": "Nigeria", "US": "United States", "GB": "United Kingdom", "CA": "Canada",
    "KE": "Kenya", "GH": "Ghana", "ZA": "South Africa", "EG": "Egypt",
    "IN": "India", "CN": "China", "JP": "Japan", "BR": "Brazil",
    "MX": "Mexico", "DE": "Germany", "FR": "France", "IT": "Italy",
    "ES": "Spain", "NL": "Netherlands", "BE": "Belgium", "SE": "Sweden",
    "NO": "Norway", "DK": "Denmark", "FI": "Finland", "PL": "Poland",
    "RU": "Russia", "UA": "Ukraine", "TR": "Turkey", "SA": "Saudi Arabia",
    "AE": "United Arab Emirates", "SG": "Singapore", "MY": "Malaysia", "ID": "Indonesia",
    "TH": "Thailand", "VN": "Vietnam", "PH": "Philippines", "KR": "South Korea",
    "AU": "Australia", "NZ": "New Zealand", "AR": "Argentina", "CL": "Chile",
    "CO": "Colombia", "PE": "Peru", "VE": "Venezuela", "NG": "Nigeria",
    "BJ": "Benin", "TZ": "Tanzania", "UG": "Uganda", "ET": "Ethiopia",
    "CM": "Cameroon", "SN": "Senegal", "CI": "Ivory Coast", "MG": "Madagascar",
    "MO": "Morocco", "DZ": "Algeria", "TN": "Tunisia", " LY": "Libya",
    "SD": "Sudan", "MA": "Ethiopia", "ZW": "Zimbabwe", "ZM": "Zambia",
    "MW": "Malawi", "MZ": "Mozambique", "BW": "Botswana", "NA": "Namibia",
    "AO": "Angola", "CD": "Democratic Republic of Congo", "RW": "Rwanda",
    "LS": "Lesotho", "SZ": "Eswatini", "MU": "Mauritius", "SC": "Seychelles",
    "PT": "Portugal", "CH": "Switzerland", "AT": "Austria", "IE": "Ireland",
    "GR": "Greece", "HU": "Hungary", "CZ": "Czech Republic", "RO": "Romania",
    "BG": "Bulgaria", "HR": "Croatia", "RS": "Serbia", "SK": "Slovakia",
    "SI": "Slovenia", "LT": "Lithuania", "LV": "Latvia", "EE": "Estonia",
    "IS": "Iceland", "LU": "Luxembourg", "MT": "Malta", "CY": "Cyprus",
    "PA": "Panama", "CR": "Costa Rica", "GT": "Guatemala", "HN": "Honduras",
    "SV": "El Salvador", "NI": "Nicaragua", "DO": "Dominican Republic", "CU": "Cuba",
    "JM": "Jamaica", "TT": "Trinidad and Tobago", "BB": "Barbados", "BS": "Bahamas",
    "BZ": "Belize", "GY": "Guyana", "SR": "Suriname", "BO": "Bolivia", "PY": "Paraguay",
    "UY": "Uruguay", "EC": "Ecuador", "GH": "Ghana"
}

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid7()))
    name = Column(String, unique=True, index=True, nullable=False)
    gender = Column(String)
    gender_probability = Column(Float)
    sample_size = Column(Integer)
    age = Column(Integer)
    age_group = Column(String)
    country_id = Column(String)
    country_name = Column(String)
    country_probability = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

def init_db():
    Base.metadata.create_all(bind=engine)