import React from 'react';
import { View, Button, StyleSheet } from 'react-native';

const MusicControls = ({ onAddToQueue, onPlayMusic, onStopMusic, onResumeMusic, isPlaying }) => {
  return (
    <View style={styles.controlsContainer}>
      <Button title="Add to Left Queue" onPress={() => onAddToQueue('left')} />
      <Button title="Add to Right Queue" onPress={() => onAddToQueue('right')} />
      <Button title="Add to Both Queue" onPress={() => onAddToQueue('both')} />
      <Button title="Play Left" onPress={() => onPlayMusic('left')} />
      <Button title="Play Right" onPress={() => onPlayMusic('right')} />
      <Button title="Play Both" onPress={() => onPlayMusic('both')} />
      <Button title="Stop Music" onPress={onStopMusic} disabled={!isPlaying} />
      <Button title="Resume Music" onPress={onResumeMusic} disabled={isPlaying} />
    </View>
  );
};

const styles = StyleSheet.create({
  controlsContainer: {
    marginBottom: 20
  }
});

export default MusicControls;
