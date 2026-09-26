from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from .database import SessionLocal
from .domain import Category, Priority, Status
from .repositories.complaints import ComplaintRepository

NAMESPACE = uuid.UUID('8e12a447-7f65-4c1b-84ee-e3b3f0ca1122')

SEED_DATA: list[tuple[str, str, Category, Priority]] = [
    ('Main water pipe burst since fajr, pani entering ground floor shops.', 'Street 12, Rawalpindi', Category.WATER, Priority.HIGH),
    ('Water supply line leaking near masjid gate, road is getting slippery.', 'Satellite Town Block B', Category.WATER, Priority.NORMAL),
    ('No water pressure for three days, please check line in our gali.', 'Gulbahar, Peshawar', Category.WATER, Priority.NORMAL),
    ('Dirty pani coming from municipal line, smell is very bad.', 'Nowshera Cantt', Category.WATER, Priority.HIGH),
    ('Small water leak from valve near park, please repair when possible.', 'Hayatabad Phase 3', Category.WATER, Priority.LOW),
    ('Transformer is sparking and wires are hanging low, bachay pass nearby.', 'University Road, Peshawar', Category.ELECTRICITY, Priority.HIGH),
    ('Bijli pole light wire is loose after rain.', 'Mardan City', Category.ELECTRICITY, Priority.NORMAL),
    ('Power cable cover damaged outside market, live wire danger.', 'Kohat Bazaar', Category.ELECTRICITY, Priority.HIGH),
    ('Street has repeated low voltage issue at evening time.', 'Charsadda Road', Category.ELECTRICITY, Priority.NORMAL),
    ('Electric box door is open near school boundary.', 'Swabi Main Road', Category.ELECTRICITY, Priority.HIGH),
    ('Kachra not collected for four days and dogs are spreading waste.', 'Bannu City', Category.SANITATION, Priority.NORMAL),
    ('Drain overflowing badly after rain, dirty water outside houses.', 'DI Khan Circular Road', Category.SANITATION, Priority.HIGH),
    ('Garbage container is full near bazaar entrance.', 'Mingora Main Bazaar', Category.SANITATION, Priority.NORMAL),
    ('Sewerage smell coming from blocked manhole, please clean.', 'Attock City', Category.SANITATION, Priority.NORMAL),
    ('Routine waste pickup missed in our street.', 'Timergara', Category.SANITATION, Priority.LOW),
    ('Big pothole caused two bike accidents today.', 'GT Road Service Lane, Nowshera', Category.ROADS, Priority.HIGH),
    ('Road broken near school gate, vans cannot pass safely.', 'Peshawar Cantt', Category.ROADS, Priority.HIGH),
    ('Small crack and rough patch on street, needs repair.', 'Mardan Sheikh Maltoon', Category.ROADS, Priority.LOW),
    ('Footpath tiles damaged outside hospital.', 'Khyber Road, Peshawar', Category.ROADS, Priority.NORMAL),
    ('Gadda on main road getting bigger after every rain.', 'Swat Road, Chakdara', Category.ROADS, Priority.NORMAL),
    ('Three street lights not working, area becomes dark after maghrib.', 'Hayatabad Phase 1', Category.STREETLIGHTS, Priority.NORMAL),
    ('Streetlight pole is leaning after storm and may fall.', 'Gilgit Jutial', Category.STREETLIGHTS, Priority.HIGH),
    ('One light is dim near community park.', 'Askari Colony, Peshawar', Category.STREETLIGHTS, Priority.LOW),
    ('Lamp outside girls school not working for one week.', 'Mardan College Chowk', Category.STREETLIGHTS, Priority.NORMAL),
    ('Street lights remain on during daytime, please inspect timer.', 'Mingora Bypass', Category.STREETLIGHTS, Priority.LOW),
    ('Stray animals blocking road near market every evening.', 'Takht Bhai Bazaar', Category.OTHER, Priority.NORMAL),
    ('Public park swing broken and sharp metal exposed.', 'Charsadda City Park', Category.OTHER, Priority.HIGH),
    ('Municipal signboard has fallen after strong wind.', 'Kohat Development Area', Category.OTHER, Priority.NORMAL),
    ('Tree branch blocking pedestrian path outside office.', 'Abbottabad Road', Category.OTHER, Priority.NORMAL),
    ('Noise from municipal generator continues late night.', 'Peshawar City', Category.OTHER, Priority.LOW),
    ('Water main leakage spreading on road near chowk.', 'Haripur Main Chowk', Category.WATER, Priority.HIGH),
    ('Transformer oil leaking and smell coming from pole.', 'Risalpur', Category.ELECTRICITY, Priority.HIGH),
    ('Open manhole without cover in middle of gali.', 'Peshawar City, Gulberg', Category.SANITATION, Priority.HIGH),
    ('Road shoulder washed away and cars moving dangerously.', 'Besham Road', Category.ROADS, Priority.HIGH),
    ('Street light completely off near bus stop.', 'Gilgit City', Category.STREETLIGHTS, Priority.NORMAL),
    ('Public bench broken in family park, please arrange repair.', 'Saidu Sharif', Category.OTHER, Priority.LOW),
]


def seed() -> int:
    now = datetime.now(timezone.utc)
    rows = []
    for index, (text, location, category, priority) in enumerate(SEED_DATA):
        rows.append(
            {
                'id': uuid.uuid5(NAMESPACE, f'{text}|{location}'),
                'text': text,
                'location': location,
                'reporter_contact': None,
                'category': category.value,
                'priority': priority.value,
                'status': Status.OPEN.value,
                'ai_summary': text[:140],
                'triaged_by': 'rules',
                'triage_latency_ms': 1,
                'created_at': now - timedelta(hours=index),
                'updated_at': now - timedelta(hours=index),
            }
        )
    with SessionLocal() as session:
        return ComplaintRepository(session).ensure_seed(rows)


if __name__ == '__main__':
    inserted = seed()
    print(f'Seed complete; inserted {inserted} rows (idempotent).')
