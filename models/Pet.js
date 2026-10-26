const mongoose = require("mongoose");

const petSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, "Name is required"],
        trim: true
    },
    species: {
        type: String,
        enum: ['dog', 'cat', 'bird', 'rabbit', 'other'],
        default: 'other'
    },
    age: {
        type: Number,
        required: [true, "Age is required"],
        min: 0,
        max: 30
    },
    adopted: {
        type: Boolean,
        default: false
    },
    adoptedOn: {
        type: Date,
        default: null
    },
    arrivedOn: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps : true
});

module.exports = mongoose.model("Pet", petSchema)
