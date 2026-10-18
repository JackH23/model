// Add an entry here and place its GLB and preview under public/models/.
export const models = [
  {
    id: 'robo-jack', name: 'Robo-Jack', category: 'Character / Mecha',
    description: 'Ivory armor. Gold accents. One curious machine. Explore its complete mechanical assembly.',
    file: 'models/robo-jack.glb', preview: 'models/robo-jack-preview.png',
    partCount: 387, grouping: 'robot', badge: 'RJ',
  },
];
export const assetUrl = (path) => `${import.meta.env.BASE_URL}${path}`;
