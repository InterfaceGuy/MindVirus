import importlib
import pydeation.imports
importlib.reload(pydeation.imports)
from pydeation.imports import *
from MolochEye.MolochEye import MolochEye


class MolochEye(CustomObject):

    def specify_parts(self):
        self.upper_eyelid = Arc(
            start_angle=PI / 6, end_angle=5 * PI / 6, radius=200, y=-100, color=WHITE)
        self.lower_eyelid = Arc(
            start_angle=7 * PI / 6, end_angle=11 * PI / 6, radius=200, y=100, color=WHITE)
        self.iris = Circle(radius=100, color=WHITE)
        self.cube_pupil_outer = Square(creation=True, size=90, color=BLUE)
        self.cube_pupil_inner = Square(creation=True, size=60, color=BLUE)
        self.cube_pupil_line_top_right = Line(
            (self.cube_pupil_outer.size / 2, self.cube_pupil_outer.size / 2), (self.cube_pupil_inner.size / 2, self.cube_pupil_inner.size / 2), color=BLUE)
        self.cube_pupil_line_bottom_right = Line(
            (self.cube_pupil_outer.size / 2, -self.cube_pupil_outer.size / 2), (self.cube_pupil_inner.size / 2, -self.cube_pupil_inner.size / 2), color=BLUE)
        self.cube_pupil_line_top_left = Line(
            (-self.cube_pupil_outer.size / 2, self.cube_pupil_outer.size / 2), (-self.cube_pupil_inner.size / 2, self.cube_pupil_inner.size / 2), color=BLUE)
        self.cube_pupil_line_bottom_left = Line(
            (-self.cube_pupil_outer.size / 2, -self.cube_pupil_outer.size / 2), (-self.cube_pupil_inner.size / 2, -self.cube_pupil_inner.size / 2), color=BLUE)
        self.parts += [self.upper_eyelid, self.lower_eyelid,
                       self.iris, self.cube_pupil_outer, self.cube_pupil_inner, self.cube_pupil_line_top_right, self.cube_pupil_line_bottom_right, self.cube_pupil_line_top_left, self.cube_pupil_line_bottom_left]

    def specify_creation(self):
        self.inherit_creation()


class MindVirus(CustomObject):

    def specify_parts(self):
        self.foldable_cube = FoldableCube(
            creation=True, z=-50, h=PI, p=PI / 2, drive_opacity=False, color=BLUE)
        self.moloch_eye = Circle(creation=True, radius=25, z=-50, color=BLUE)
        self.parts = [self.foldable_cube, self.moloch_eye]

    def specify_parameters(self):
        self.forward_parameter = UCompletion(name="Forward", default_value=0)
        self.parameters += [self.forward_parameter]

    def specify_relations(self):
        self.forward_relation_cube = XRelation(part=self.foldable_cube, whole=self, desc_ids=[POS_Z],
                                               parameters=[self.forward_parameter], formula=f"-50 - 50 * {self.forward_parameter.name}")
        self.forward_relation_eye = XRelation(part=self.moloch_eye, whole=self, desc_ids=[POS_Z],
                                              parameters=[self.forward_parameter], formula=f"-50 - 50 * {self.forward_parameter.name}")

    def specify_action_parameters(self):
        self.thrust_parameter = UCompletion(name="Thrust", default_value=0)
        self.action_parameters += [self.thrust_parameter]

    def specify_actions(self):
        # Define the thrust action for the foldable cube
        thrust_action = XAction(
            Movement(self.foldable_cube.fold_parameter, (0, 1),
                     output=(0, 1), part=self.foldable_cube),
            Movement(self.forward_parameter, (0, 1), output=(0, 1)),
            target=self, completion_parameter=self.thrust_parameter, name="Thrust")

    def specify_creation(self):
        self.inherit_creation()

    def thrust(self, completion=1):
        """specifies the thrust animation"""
        desc_id = self.thrust_parameter.desc_id
        animation = ScalarAnimation(
            target=self, descriptor=desc_id, value_fin=completion)
        self.obj[desc_id] = completion
        return animation


class Cable(CustomObject):
    """A cable that connects two objects with a smooth spline curve guided by normal vectors."""

    def __init__(self, start_point=(-50, 0, 0), end_point=(50, 0, 0), start_normal=(25, 0, 0), end_normal=(-25, 0, 0), **kwargs):
        self.start_point = start_point
        self.end_point = end_point
        self.start_normal = start_normal
        self.end_normal = end_normal
        super().__init__(**kwargs)

    def specify_parts(self):
        self.start_point_null = Null(name="StartPoint")
        self.start_point_null.set_position(position=self.start_point)
        self.start_normal_null = Null(name="StartNormal")
        self.start_normal_null.set_position(position=self.start_normal)
        self.start_normal_null.obj.InsertUnder(self.start_point_null.obj)
        self.end_point_null = Null(name="EndPoint")
        self.end_point_null.set_position(position=self.end_point)
        self.end_normal_null = Null(name="EndNormal")
        self.end_normal_null.set_position(position=self.end_normal)
        self.end_normal_null.obj.InsertUnder(self.end_point_null.obj)
        self.tracer = Tracer(self.start_point_null, self.start_normal_null, self.end_normal_null,
                             self.end_point_null, tracing_mode="objects", spline_type="b-spline")
        self.cable_profile = Circle(radius=1, helper_mode=True)
        self.sweep_nurbs = SweepNurbs(
            rail=self.tracer, profile=self.cable_profile, name="Cable", outline_only=True, fill_color=BLACK)
        self.parts = [self.start_point_null, self.start_normal_null, self.end_point_null,
                      self.end_normal_null, self.tracer, self.cable_profile, self.sweep_nurbs]

    def specify_parameters(self):
        self.start_growth_parameter = UCompletion(
            name="Start", default_value=0)
        self.end_growth_parameter = UCompletion(name="End", default_value=1)
        self.parameters += [self.start_growth_parameter,
                            self.end_growth_parameter]

    def specify_relations(self):
        self.start_growth_relation = XRelation(part=self.sweep_nurbs, whole=self, desc_ids=[self.sweep_nurbs.desc_ids["start_growth"]],
                                               parameters=[self.start_growth_parameter], formula=f"{self.start_growth_parameter.name}")
        self.end_growth_relation = XRelation(part=self.sweep_nurbs, whole=self, desc_ids=[self.sweep_nurbs.desc_ids["end_growth"]],
                                             parameters=[self.end_growth_parameter], formula=f"{self.end_growth_parameter.name}")

    def specify_creation(self):
        self.creation_action = XAction(
            Movement(self.sweep_nurbs.creation_parameter, (0, 1),
                     output=(0, 1), part=self.sweep_nurbs),
            target=self, completion_parameter=self.creation_parameter, name="Creation")


class MindVirusJourney(CustomObject):

    def specify_parts(self):
        self.mind_virus = MindVirus(h=PI / 2)
        self.mind_virus.thrust()
        self.path = Cable()
        self.mind_virus.align_to_spline(spline=self.path.tracer)
        self.parts = [self.mind_virus, self.path]

    def specify_creation(self):
        self.inherit_creation()

    def specify_parameters(self):
        self.journey_completion_parameter = UCompletion(
            name="JourneyCompletion", default_value=1)
        self.parameters += [self.journey_completion_parameter]

    def specify_relations(self):
        self.cable_completion_relation = XRelation(part=self.path, whole=self, desc_ids=[self.path.end_growth_parameter.desc_id],
                                                   parameters=[self.journey_completion_parameter], formula=f"{self.journey_completion_parameter.name}")
        self.mind_virus_completion_relation = XRelation(part=self.mind_virus.align_to_spline_tag, whole=self, desc_ids=[self.mind_virus.align_to_spline_tag.desc_ids["position"]],
                                                        parameters=[self.journey_completion_parameter], formula=f"{self.journey_completion_parameter.name}")


if __name__ == "__main__":
    #mind_virus = MindVirus()
    #cable = Cable(creation=True)
    #mind_virus_journey = MindVirusJourney(creation=True)
    moloch_eye = MolochEye(creation=True)
