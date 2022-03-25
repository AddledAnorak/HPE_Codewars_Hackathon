class Hospital {
    constructor(name, addr, phone, email, currStars, website = '') {
        this.name = name;
        this.addr = addr;
        this.phoneNumber = phone;
        this.emailId = email;
        this.stars = currStars;
        this.website = website;
        this.hasWebsite = website !== '';
    }
}