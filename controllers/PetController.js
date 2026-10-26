const Pet=require('../models/Pet');

exports.getPets=async(req, res, next) => {
    try{
        const filter={};
        if (req.query.species) filter.species=req.query.species;
        if (req.query.adopted==="true") filter.adopted=true;
        if (req.query.adopted==="false") filter.adopted=false;

        let query=Pet.find(filter);

        if (req.query.sort==="age") query=query.sort({age:1});
        else if (req.query.sort==="name") query=query.sort({name:1});
        else query=query.sort({createdAt:-1});

        const pets=await query;
        res.status(200).json(pets);
    }catch(err){
        next(err);
    }
};

exports.getAvailablePets=async(req, res, next) => {
    try{
        const pets=await Pet.find({adopted:false});
        res.status(200).json(pets);
    }catch(err){
        next(err);
    }
};

exports.getPet=async(req, res, next) => {
    try {
        const pet=await Pet.findById(req.params.id);
        if (!pet) {
            return res.status(404).json({ 
                message:"Pet not found" 
            });
        }
        res.status(200).json(pet);
    } catch (err) {
        next(err);
    }
};

exports.createPet=async(req, res, next) => {
    try {
        const pet = new Pet(req.body);
        const savedPet = await pet.save();
        res.status(201).json(savedPet);
    } catch (err) {
        next(err);
    }
};

exports.updatePet=async(req, res, next) => {
    try {
        const existing = await Pet.findById(req.params.id);
        if (!existing) {
            return res.status(404).json({ 
                message:"Pet not found" 
            });
        }
        const update = { ...req.body };
        if (typeof update.adopted === "boolean" && update.adopted !== existing.adopted) {
            update.adoptedOn = update.adopted ? new Date() : null;
        }
        const pet = await Pet.findByIdAndUpdate(req.params.id, update, {
            new: true,runValidators: true
        });
        res.status(200).json(pet);
    } catch (err) {
        next(err);
    }
};

exports.deletePet=async (req, res, next) => {
    try {
        const pet=await Pet.findByIdAndDelete(req.params.id);
        if (!pet) {
            return res.status(404).json({
                message:"Pet not found"
            });
        }
        res.status(200).json({
            message:"Pet has deleted successfully!!"    
        });
    } catch (err) {
        next(err);
    }
};