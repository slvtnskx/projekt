const { readFileSync, writeFileSync } = require("fs")

const locationMap = new Map(JSON.parse(readFileSync("./locationMap.json")))

function calculateWage(item, targetType, sourceField) {
    if (!item[sourceField]) return null
    
    const currentType = item.typMzdy?.id.split("/")[1]
    if (currentType === targetType) return Math.round(item[sourceField] * 100) / 100
    
    const hoursPerWeek = item.pocetHodinTydne || 40
        
    if (!hoursPerWeek) return null
    
    const monthlyHours = hoursPerWeek * 4
    const result = targetType === "hod" ? 
        item[sourceField] / monthlyHours :
        item[sourceField] * monthlyHours
        
    return Math.round(result * 100) / 100
}

function findID(idToUse, typeToFind){
    const found = locationMap.get(idToUse)
    if (!found) {console.log(idToUse, typeToFind)}
    return found[typeToFind]
}

function getLocationIDs(item) { 
        if (item.mistoVykonuPrace?.typMistaVykonuPrace?.id.split("/")[1] == "adrprov" && item.mistoVykonuPrace?.pracoviste[0].adresa) {
            let regionID = item.mistoVykonuPrace?.pracoviste[0].adresa?.kraj?.id.split("/")[1] ?? null
            let districtID = item.mistoVykonuPrace?.pracoviste[0].adresa?.okres?.id.split("/")[1] ?? null
            let municipalityID = item.mistoVykonuPrace?.pracoviste[0].adresa?.obec?.id.split("/")[1] ?? null
            let cityPartID = item.mistoVykonuPrace?.pracoviste[0].adresa?.mestskyObvodMestskaCast?.id.split("/")[1] ?? null
            let muniPartID = item.mistoVykonuPrace?.pracoviste[0].adresa?.castObce?.id.split("/")[1] ?? null
            
            regionID = regionID ? "reg"+regionID : null
            districtID = districtID ? "dist"+districtID : null
            municipalityID = municipalityID ? "muni"+municipalityID : null
            cityPartID = cityPartID ? "cityPart"+cityPartID : null
            muniPartID = muniPartID ? "muniPart"+muniPartID : null

            if ((!municipalityID) && cityPartID){
                municipalityID = findID(cityPartID, "municipality")
            }
            if ((!districtID) && municipalityID){
                districtID = findID(municipalityID, "district")
            }
            if ((!regionID) && districtID){
                regionID = findID(districtID, "region")
            }
            
            return {
                region: regionID,
                district: districtID,
                municipality: municipalityID,
                cityPart: cityPartID
            }
        } else {
            return {}
        }        
}



class RestructuredOffer {
    constructor(item){
        let locations = getLocationIDs(item)
        this.id = Number(item.portalId),
        this.lastModified = item.datumZmeny,
        this.minWageHourly = calculateWage(item, "hod", "mesicniMzdaOd"),
        this.minWageMonthly = calculateWage(item, "mesic", "mesicniMzdaOd"), 
        this.region = locations.region ?? null,
        this.district = locations.district ?? null,
        this.municipality = locations.municipality ?? null,
        this.cityPart = locations.cityPart ?? null,
        this.profession = item.profeseCzIsco.id.split("/")[1] ?? null, 
        this.textToSearch = item.pozadovanaProfese.cs + "\n" + item.upresnujiciInformace?.cs,
        this.education = item.minPozadovaneVzdelani?.id.split("/")[1] ?? null,
        this.shifts = item.smennost?.id.split("/")[1] ?? null,
        this.hours = item.pocetHodinTydne ?? null,
        this.fullTime = item.pracovnePravniVztahy?.id?.split("/")[1] == "plny" ? true : false,
        this.partTime = item.pracovnePravniVztahy?.id?.split("/")[1] == "zkraceny" ? true : false,
        this.freelanceWork = item.pracovnePravniVztahy?.id?.split("/")[1] == "dpp" ? true : false,
        this.shortTermEmployment = item.pracovnePravniVztahy?.id?.split("/")[1] == "dpc" ? true : false,
        this.civilService = item.pracovnePravniVztahy?.id?.split("/")[1] == "sluzebni" ? true : false,
        this.agencyContract = item.souhlasAgenturyAgentura ?? false,
        this.agencyTemporaryStaffing = item.souhlasAgenturyUzivatel ?? false,
        this.asylumSeeker = item.azylant ?? false,
        this.nonEUnational = item.cizinecMimoEu ?? false,
        this.blueCard = item.modraKarta ?? false,
        this.employeeCard = item.zamestnaneckaKarta ?? false,
        this.displayInformation = {}
    }
}

function restructure(data){
    const results = data.map((item, index) => {
        return new RestructuredOffer(item)
    })
    return results
}

let data = JSON.parse(readFileSync("./volna-mista.json")).polozky
console.log("loaded data")
let res = JSON.stringify(restructure(data), null, 2)
writeFileSync("job_offers.json", res)
console.log("finished")