import random
from uuid6 import uuid7
import models
from models import SessionLocal, init_db, Profile, COUNTRY_MAP

MALE_FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
    "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
    "Kenneth", "Kevin", "Brian", "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan",
    "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
    "Benjamin", "Samuel", "Raymond", "Gregory", "Frank", "Alexander", "Patrick", "Jack", "Dennis", "Jerry",
    "Aaron", "Jose", "Adam", "Nathan", "Henry", "Zachary", "Douglas", "Peter", "Kyle", "Noah", "Ethan",
    "Jeremy", "Walter", "Christian", "Keith", "Roger", "Terry", "Austin", "Sean", "Gerald", "Carl",
    "Harold", "Dylan", "Arthur", "Lawrence", "Jordan", "Jesse", "Bryan", "Billy", "Bruce", "Gabriel",
    "Joe", "Logan", "Albert", "Willie", "Alan", "Eugene", "Russell", "Vincent", "Philip", "Bobby", "Johnny"
]

FEMALE_FIRST_NAMES = [
    "Mary", "Jennifer", "Linda", "Patricia", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Lisa",
    "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Dorothy",
    "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Kathleen",
    "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole", "Helen", "Samantha",
    "Katherine", "Christine", "Debra", "Rachel", "Carolyn", "Janet", "Catherine", "Maria", "Heather", "Diane",
    "Ruth", "Julie", "Olivia", "Joyce", "Virginia", "Victoria", "Kelly", "Lauren", "Christina", "Joan",
    "Evelyn", "Judith", "Megan", "Andrea", "Cheryl", "Hannah", "Jacqueline", "Martha", "Gloria", "Teresa",
    "Ann", "Sara", "Madison", "Frances", "Kathryn", "Janice", "Jean", "Abigail", "Alice", "Judy", "Sophia",
    "Grace", "Denise", "Amber", "Doris", "Marilyn", "Danielle", "Beverly", "Isabella", "Theresa", "Diana", "Natalie"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

def get_age_group(age):
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    else:
        return "senior"

def seed_database(num_profiles=2026):
    init_db()
    db = SessionLocal()
    
    existing = db.query(Profile).count()
    if existing >= num_profiles:
        print(f"Database already has {existing} profiles")
        db.close()
        return
    
    country_ids = list(COUNTRY_MAP.keys())
    created = 0
    
    all_names = set()
    for p in db.query(Profile.name).all():
        all_names.add(p[0])
    
    while created < num_profiles:
        gender = random.choice(["male", "female"])
        first_name = random.choice(MALE_FIRST_NAMES if gender == "male" else FEMALE_FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        suffix = random.randint(1, 9999)
        name = f"{first_name} {last_name} {suffix}"
        
        if name in all_names:
            continue
        all_names.add(name)
        
        age = random.randint(1, 85)
        country_id = random.choice(country_ids)
        country_name = COUNTRY_MAP.get(country_id, country_id)
        
        profile = Profile(
            id=str(uuid7()),
            name=name,
            gender=gender,
            gender_probability=round(random.uniform(0.5, 1.0), 2),
            sample_size=random.randint(1000, 5000000),
            age=age,
            age_group=get_age_group(age),
            country_id=country_id,
            country_name=country_name,
            country_probability=round(random.uniform(0.1, 0.9), 2)
        )
        db.add(profile)
        db.commit()
        created += 1
        
        if created % 100 == 0:
            print(f"Created {created} profiles...")
    
    db.close()
    print(f"Created {created} profiles total")

if __name__ == "__main__":
    seed_database()