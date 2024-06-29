import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import { Audio } from 'expo-av';
import axios from 'axios';
import QueueList from './components/QueueList';
import MusicControls from './components/MusicControls';

const App = () => {
  const [url, setUrl] = useState('');
  const [queue, setQueue] = useState([]);
  const [sound, setSound] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleAddToQueue = async (channel) => {
    try {
      const response = await axios.post('http://192.168.1.14:5000/api/add-to-queue', { url, channel });
      const filename = response.data.filename;
      setQueue([...queue, { filename, channel }]);
    } catch (error) {
      console.error(error);
    }
  };

  const handlePlayMusic = async (channel) => {
    if (sound) {
      await sound.unloadAsync();
      setSound(null);
    }

    const filteredQueue = queue.filter(item => item.channel === channel || channel === 'both');

    for (let item of filteredQueue) {
      const { filename } = item;
      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri: `http://192.168.1.14:5000/songs/${filename}` },
        { shouldPlay: true }
      );
      setSound(newSound);

      // Adjust volume to play in the correct channel
      if (channel === 'left') {
        await newSound.setVolumeAsync(1.0);
        await newSound.setPanAsync(-1.0);  // Full left
      } else if (channel === 'right') {
        await newSound.setVolumeAsync(1.0);
        await newSound.setPanAsync(1.0);  // Full right
      } else {
        await newSound.setVolumeAsync(1.0);
        await newSound.setPanAsync(0.0);  // Center
      }

      await newSound.playAsync();
      setIsPlaying(true);
    }
  };

  const handleStopMusic = async () => {
    if (sound) {
      await sound.pauseAsync();
      setIsPlaying(false);
    }
  };

  const handleResumeMusic = async () => {
    if (sound) {
      await sound.playAsync();
      setIsPlaying(true);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Music Player</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter YouTube URL"
        value={url}
        onChangeText={setUrl}
      />
      <MusicControls
        onAddToQueue={handleAddToQueue}
        onPlayMusic={handlePlayMusic}
        onStopMusic={handleStopMusic}
        onResumeMusic={handleResumeMusic}
        isPlaying={isPlaying}
      />
      <QueueList queue={queue} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 10,
    paddingHorizontal: 10
  }
});

export default App;
