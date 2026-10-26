const express = require('express');
const c = require('../controllers/PetController');
const router = express.Router();
const validId = require('../middleware/validId');

router.get('/', c.getPets);
router.get('/available', c.getAvailablePets);

router.post('/', c.createPet);

router.get('/:id', validId, c.getPet);

router.put('/:id', validId, c.updatePet);

router.delete('/:id', validId, c.deletePet);

module.exports = router;