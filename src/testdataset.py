from sessionprogress import SessionProgress
from systemprogress import SystemProgress

def create_sample_session_progress() -> SessionProgress:
    """
    Creates and returns a populated instance of the SessionProgress class with sample data.
    """
    session = SessionProgress(
        earned_merits=100,
        time=3600,
        is_docking_event=1,
        power_play_rank=5,
        power_play="Denton Patreus"
    )

    # Add sample activities
    session.activities.add_unknown_merits(10)
    session.activities.add_ship_scan_merits(20)
    session.activities.add_bounty_merits(30)
    session.activities.add_powerplay_delivery_merits(40)
    session.activities.add_donation_mission_merits(50)

    # Add sample commodities
    session.add_commodity(SessionProgress.Commodities(
        type="Gold",
        type_localised="Gold (Localized)",
        delivered_system="Sol",
        collected=100,
        delivered=50
    ))
    session.add_commodity(SessionProgress.Commodities(
        type="Silver",
        type_localised="Silver (Localized)",
        delivered_system="Alpha Centauri",
        collected=200,
        delivered=150
    ))

    return session

def create_sample_system_progress_list() -> list[SystemProgress]:
    """
    Creates and returns a list of populated SystemProgress objects with sample data.
    """
    systems = []

    # Example 1
    system1 = SystemProgress()
    system1.system = "Sol"
    system1.earnings = 5000.0
    system1.controlling_power = "Denton Patreus"
    system1.power_play_state = "Fortified"
    system1.power_play_state_control_progress = 0.75
    system1.power_play_state_reinforcement = 12000.0
    system1.power_play_state_undermining = 500.0
    system1.orig_power_play_state_control_progress = 0.50
    system1.orig_power_play_state_reinforcement = 10000.0
    system1.orig_power_play_state_undermining = 300.0
    systems.append(system1)

    # Example 2
    system2 = SystemProgress()
    system2.system = "Alpha Centauri"
    system2.earnings = 3000.0
    system2.controlling_power = "Aisling Duval"
    system2.power_play_state = "Exploited"
    system2.power_play_state_control_progress = 0.60
    system2.power_play_state_reinforcement = 8000.0
    system2.power_play_state_undermining = 200.0
    system2.orig_power_play_state_control_progress = 0.40
    system2.orig_power_play_state_reinforcement = 7000.0
    system2.orig_power_play_state_undermining = 100.0
    systems.append(system2)

    # Example 3
    system3 = SystemProgress()
    system3.system = "Lave"
    system3.earnings = 7000.0
    system3.controlling_power = "Zachary Hudson"
    system3.power_play_state = "Contested"
    system3.power_play_state_control_progress = 0.30
    system3.power_play_state_reinforcement = 5000.0
    system3.power_play_state_undermining = 1000.0
    system3.orig_power_play_state_control_progress = 0.20
    system3.orig_power_play_state_reinforcement = 4000.0
    system3.orig_power_play_state_undermining = 800.0
    systems.append(system3)

    # Example 4
    system4 = SystemProgress()
    system4.system = "Eranin"
    system4.earnings = 2000.0
    system4.controlling_power = "Edmund Mahon"
    system4.power_play_state = "Controlled"
    system4.power_play_state_control_progress = 0.90
    system4.power_play_state_reinforcement = 15000.0
    system4.power_play_state_undermining = 300.0
    system4.orig_power_play_state_control_progress = 0.85
    system4.orig_power_play_state_reinforcement = 14000.0
    system4.orig_power_play_state_undermining = 200.0
    systems.append(system4)

    # Example 5
    system5 = SystemProgress()
    system5.system = "Leesti"
    system5.earnings = 1000.0
    system5.controlling_power = "Pranav Antal"
    system5.power_play_state = "Exploited"
    system5.power_play_state_control_progress = 0.50
    system5.power_play_state_reinforcement = 6000.0
    system5.power_play_state_undermining = 400.0
    system5.orig_power_play_state_control_progress = 0.45
    system5.orig_power_play_state_reinforcement = 5500.0
    system5.orig_power_play_state_undermining = 300.0
    systems.append(system5)

    return systems