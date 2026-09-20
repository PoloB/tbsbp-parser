"""Tests for parser."""

import pathlib
import types

import pytest

from tbsbpparser import parse
from tbsbpparser.parser import SBoardAudioClip
from tbsbpparser.parser import SBoardAudioTrack
from tbsbpparser.parser import SBoardLayer
from tbsbpparser.parser import SBoardLibrary
from tbsbpparser.parser import SBoardLibraryCategory
from tbsbpparser.parser import SBoardLibraryElement
from tbsbpparser.parser import SBoardPanel
from tbsbpparser.parser import SBoardProject
from tbsbpparser.parser import SBoardScene
from tbsbpparser.parser import SBoardSequence
from tbsbpparser.parser import SBoardTimeline
from tbsbpparser.parser import SBoardTransition
from tbsbpparser.parser import SBoardVideoClip
from tbsbpparser.parser import SBoardVideoTrack

from .conftest import SAMPLE_DIRECTORY
from .conftest import TESTED_FILES


def _test_project(project: SBoardProject) -> None:
    # Try to get the scenes from project
    scenes_gen = project.scenes
    assert isinstance(scenes_gen, types.GeneratorType)

    for s in scenes_gen:
        assert isinstance(s, SBoardScene)

        # Test scene
        _test_scene(s)

    sequence_gen = project.sequences
    assert isinstance(sequence_gen, types.GeneratorType)

    for sq in sequence_gen:
        assert isinstance(sq, SBoardSequence)
        _test_sequence(sq)

    # Test timeline
    assert isinstance(project.timeline, SBoardTimeline)
    _test_timeline(project.timeline)

    # Test library
    library = project.library
    assert isinstance(library, SBoardLibrary)
    _test_library(library)

    assert isinstance(project.frame_rate, float)
    assert isinstance(project.title, str)


def _test_library(library: SBoardLibrary) -> None:

    # Test categories
    cat_gen = library.categories
    assert isinstance(cat_gen, types.GeneratorType)
    assert isinstance(library.project, SBoardProject)

    element_gen = library.elements
    assert isinstance(element_gen, types.GeneratorType)

    for element in element_gen:
        assert isinstance(element, SBoardLibraryElement)
        _test_element(element)


def _test_sequence(sequence: SBoardSequence) -> None:

    assert isinstance(sequence.name, str)
    assert isinstance(sequence.project, SBoardProject)

    for scene in sequence.scenes:
        assert isinstance(scene, SBoardScene)
        _test_scene(scene)


def _test_scene(scene: SBoardScene) -> None:

    # Test name and id
    assert isinstance(scene.name, str)
    assert isinstance(scene.uid, str)

    # Test frame ranges
    frame_range = scene.clip_range
    assert isinstance(frame_range, tuple)
    assert isinstance(frame_range[0], int)
    assert isinstance(frame_range[1], int)

    cut_range = scene.timeline_range
    assert isinstance(cut_range, tuple)
    assert isinstance(cut_range[0], int)
    assert isinstance(cut_range[1], int)

    # Test length
    assert isinstance(scene.length, int)

    # Test sequence
    assert isinstance(scene.sequence, (type(None), SBoardSequence))

    # Test panels
    panels_gen = scene.panels
    assert isinstance(panels_gen, types.GeneratorType)

    panel_length_sum = 0

    for p in panels_gen:
        assert isinstance(p, SBoardPanel)
        _test_panel(p)

        # Test scene equality
        assert p.scene == scene

        # Test range length
        panel_length_sum += p.length

    assert panel_length_sum == scene.length


def _test_panel(panel: SBoardPanel) -> None:

    # Test name and id
    assert isinstance(panel.number, int)
    assert isinstance(panel.uid, str)

    # Test scene
    assert isinstance(panel.scene, SBoardScene)

    # Test project
    assert isinstance(panel.project, SBoardProject)

    # Test frame range
    frame_range = panel.clip_range
    assert isinstance(frame_range, tuple)
    assert isinstance(frame_range[0], int)
    assert isinstance(frame_range[1], int)

    scene_range = panel.scene_range
    assert isinstance(scene_range, tuple)
    assert isinstance(scene_range[0], int)
    assert isinstance(scene_range[1], int)

    timeline_range = panel.timeline_range
    assert isinstance(timeline_range, tuple)
    assert isinstance(timeline_range[0], int)
    assert isinstance(timeline_range[1], int)

    # Test layers without groups
    layers_gen = panel.layer_iter()
    assert isinstance(layers_gen, types.GeneratorType)

    for layer in layers_gen:
        assert isinstance(layer, SBoardLayer)
        assert layer.is_group() is False
        _test_layer(layer)

    # Test all layers iter
    for layer in panel.layer_iter(groups=True, recursive=True):
        assert isinstance(layer, SBoardLayer)

        if not layer.is_group():
            _test_layer_leaf(layer)


def _test_timeline(timeline: SBoardTimeline) -> None:

    assert isinstance(timeline.uid, str)
    assert isinstance(timeline.length, int)
    assert isinstance(timeline.scenes, types.GeneratorType)

    scenes = list(timeline.scenes)
    assert len(scenes) >= 1

    # Test scenes from timeline
    current_scene_start = 0

    for s in timeline.scenes:
        assert isinstance(s, SBoardScene)
        assert s.timeline_range[0] >= current_scene_start
        current_scene_start = s.timeline_range[0]

    # Test panels from timeline
    current_panel_start = 0

    for p in timeline.panels:
        assert isinstance(p, SBoardPanel)
        assert p.timeline_range[0] >= current_panel_start
        current_panel_start = p.timeline_range[0]

    v_tracks = timeline.video_tracks
    assert isinstance(v_tracks, types.GeneratorType)

    for track in v_tracks:
        assert isinstance(track, SBoardVideoTrack)
        _test_video_track(track)

    a_tracks = timeline.audio_tracks
    assert isinstance(a_tracks, types.GeneratorType)

    for track in a_tracks:
        assert isinstance(track, SBoardAudioTrack)
        _test_audio_track(track)

    for transition in timeline.transitions:
        assert isinstance(transition, SBoardTransition)
        assert transition.timeline == timeline
        _test_transition(transition)

    assert isinstance(timeline.project, SBoardProject)


def _test_video_track(track: SBoardVideoTrack) -> None:
    assert isinstance(track.uid, str)
    assert isinstance(track.name, str)
    assert isinstance(track.timeline, SBoardTimeline)
    assert isinstance(track.is_enabled(), bool)
    clips = track.clips
    assert isinstance(clips, types.GeneratorType)

    for clip in clips:
        assert isinstance(clip, SBoardVideoClip)
        _test_video_clip(clip)


def _test_audio_track(track: SBoardAudioTrack) -> None:
    assert isinstance(track.name, str)
    assert isinstance(track.timeline, SBoardTimeline)
    assert isinstance(track.is_enabled(), bool)
    clips = track.clips
    assert isinstance(clips, types.GeneratorType)

    for clip in clips:
        assert isinstance(clip, SBoardAudioClip)
        _test_audio_clip(clip)


def _test_video_clip(clip: SBoardVideoClip) -> None:
    assert isinstance(clip.uid, str)
    assert isinstance(clip.timeline_range, tuple)
    assert isinstance(clip.clip_range, tuple)
    assert isinstance(clip.length, int)
    assert isinstance(clip.path, str)
    assert isinstance(clip.element, SBoardLibraryElement)
    assert isinstance(clip.track, SBoardVideoTrack)


def _test_audio_clip(clip: SBoardAudioClip) -> None:
    assert isinstance(clip.file_name, str)
    assert isinstance(clip.timeline_range, tuple)
    assert isinstance(clip.clip_range, tuple)
    assert isinstance(clip.length, int)
    assert isinstance(clip.path, str)
    assert isinstance(clip.track, SBoardAudioTrack)


def _test_element(element: SBoardLibraryElement) -> None:

    assert isinstance(element.category, SBoardLibraryCategory)
    assert isinstance(element.name, str)
    assert isinstance(element.path, str)


def _test_layer(layer: SBoardLayer) -> None:

    assert isinstance(layer.name, str)
    assert isinstance(layer.panel, SBoardPanel)

    element = layer.element
    assert isinstance(element, (SBoardLibraryElement, type(None)))

    if element:
        _test_element(element)


def _test_layer_leaf(layer: SBoardLayer) -> None:
    assert len(list(layer.layer_iter())) == 0


def _test_transition(transition: SBoardTransition) -> None:
    assert isinstance(transition.uid, str)
    assert isinstance(transition.timeline_range, tuple)
    assert isinstance(transition.type, str)


@pytest.mark.parametrize(
    "sboard_path",
    [SAMPLE_DIRECTORY / sboard_file for sboard_file in TESTED_FILES],
    ids=TESTED_FILES,
)
def test_project(sboard_path: pathlib.Path) -> None:
    """Test the given projects."""
    project = parse(str(sboard_path))
    _test_project(project)


def test_tracks() -> None:  # noqa: PLR0915
    """Test the content of the tracks."""
    test_path = str(SAMPLE_DIRECTORY / "track.sboard")
    project = parse(test_path)
    timeline = project.timeline

    audio_tracks = list(timeline.audio_tracks)
    video_tracks = list(timeline.video_tracks)

    # Check audio tracks
    assert len(audio_tracks) == 2  # noqa: PLR2004
    assert audio_tracks[0].name == "AudioTrack2"
    assert audio_tracks[1].name == "AudioTrack1"
    audio_clips1 = list(audio_tracks[0].clips)
    assert len(audio_clips1) == 0
    audio_clips2 = list(audio_tracks[1].clips)
    assert len(audio_clips2) == 2  # noqa: PLR2004
    audio_clip21 = audio_clips2[0]
    audio_clip22 = audio_clips2[1]
    assert audio_clip21.file_name == "file_example_MP3_700KB.mp3"
    assert audio_clip21.clip_range == (4.2083334922790527, 27.287981033325195)
    assert audio_clip21.timeline_range == (146, 699)
    assert audio_clip22.file_name == "file_example_MP3_700KB.mp3"
    assert audio_clip22.clip_range == (0, 27.287981033325195)
    assert audio_clip22.timeline_range == (775, 1429)

    assert len(video_tracks) == 2  # noqa: PLR2004
    video_track = video_tracks[0]
    assert video_track.name == "VideoTrack1"
    assert video_track.uid == "ATV-0A5A672AA5C01754"
    video_clips = list(video_track.clips)
    assert len(video_clips) == 5  # noqa: PLR2004
    video_clip1 = video_clips[0]
    video_clip2 = video_clips[1]
    video_clip3 = video_clips[2]
    assert video_clip1.uid == "0a5a672aa5c0189f"
    assert video_clip2.uid == "0a5a672aa5c04668"
    assert video_clip3.uid == "0a5a672aa5c03a09"
    assert video_clip1.length == 1045  # noqa: PLR2004
    assert video_clip2.length == 24  # noqa: PLR2004
    assert video_clip3.length == 1045  # noqa: PLR2004
    assert video_clip1.timeline_range == (1, 1045)
    assert video_clip2.timeline_range == (1046, 1069)
    assert video_clip3.timeline_range == (1203, 1491)
    assert video_clip1.clip_range == (1, 1045)
    assert video_clip2.clip_range == (1, 24)
    assert video_clip3.clip_range == (757, 1045)
    element_video_clip1 = video_clip1.element
    element_video_clip2 = video_clip2.element
    element_video_clip3 = video_clip3.element
    assert element_video_clip1.category.uid == "2"
    assert element_video_clip2.category.uid == "3"
    assert element_video_clip3.category.uid == "2"
    assert element_video_clip1.category.name == "mp4"
    assert element_video_clip2.category.name == "Shared"
    assert element_video_clip3.category.name == "mp4"
