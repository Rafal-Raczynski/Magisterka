from extract_chargers import extract_chargers
from extract_aic import extract_aic_per_capita
from extract_energy_price import extract_energy_price
from extract_oil_price_and_pl_exchange_rate import extract_oil_price_and_pl_exchange_rate
from extraxt_vehicles_number import extract_vehicles_number_new_regestration_and_percentage

def main():
     extract_aic_per_capita(
        'Poland', 'Denmark', 'Czechia', 'Germany', 'Netherlands', 'Spain'
    )
     extract_vehicles_number_new_regestration_and_percentage(
        'Polska', 'Niemcy', 'Dania', 'Czechy', 'Holandia', 'Hiszpania'
    )
     extract_energy_price(
        'Poland', 'Denmark', 'Czechia', 'Germany', 'Netherlands', 'Spain'
    )
     extract_oil_price_and_pl_exchange_rate(
        'Poland', 'Denmark', 'Czechia', 'Germany', 'Netherlands', 'Spain'
    ) 
     extract_chargers(
        'Polska', 'Niemcy', 'Dania', 'Czechy', 'Holandia', 'Hiszpania'
    )

if __name__ == "__main__":
    main()