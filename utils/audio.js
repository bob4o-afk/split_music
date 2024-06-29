import { Audio } from 'expo-av';

export const createSound = async (uri) => {
  const { sound } = await Audio.Sound.createAsync({ uri });
  return sound;
};
