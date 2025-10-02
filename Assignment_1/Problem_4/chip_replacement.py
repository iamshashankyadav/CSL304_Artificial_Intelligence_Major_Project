import random
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

random.seed(42)
np.random.seed(42)


class ChipPlacementOptimizer:
    def __init__(self, board_width, board_height, chip_specifications, chip_connections):
        self.board_width = board_width
        self.board_height = board_height
        self.chip_specs = chip_specifications
        self.connections = chip_connections
        self.optimization_history = []
        self.score_timeline = []

    def calculate_movement_boundaries(self, chip_id):
        chip_width = self.chip_specs[chip_id]['w']
        leftmost_position = 0
        rightmost_position = self.board_width - chip_width
        return leftmost_position, rightmost_position

    def compute_wire_distance(self, chip1_id, chip2_id, chip1_x, chip2_x):
        chip1_width = self.chip_specs[chip1_id]['w']
        chip2_width = self.chip_specs[chip2_id]['w']
        chip1_y = self.chip_specs[chip1_id]['y']
        chip2_y = self.chip_specs[chip2_id]['y']

        horizontal_gap = max(0, chip2_x - (chip1_x + chip1_width), chip1_x - (chip2_x + chip2_width))
        vertical_distance = abs(chip1_y - chip2_y)
        return horizontal_gap + vertical_distance

    def calculate_overlap_area(self, chip1_id, chip2_id, chip1_x, chip2_x):
        chip1_y = self.chip_specs[chip1_id]['y']
        chip1_height = self.chip_specs[chip1_id]['h']
        chip1_width = self.chip_specs[chip1_id]['w']

        chip2_y = self.chip_specs[chip2_id]['y']
        chip2_height = self.chip_specs[chip2_id]['h']
        chip2_width = self.chip_specs[chip2_id]['w']

        overlap_x_start = max(chip1_x, chip2_x)
        overlap_x_end = min(chip1_x + chip1_width - 1, chip2_x + chip2_width - 1)

        if overlap_x_end < overlap_x_start:
            return 0

        overlap_y_start = max(chip1_y, chip2_y)
        overlap_y_end = min(chip1_y + chip1_height - 1, chip2_y + chip2_height - 1)

        if overlap_y_end < overlap_y_start:
            return 0

        overlap_area = (overlap_x_end - overlap_x_start + 1) * (overlap_y_end - overlap_y_start + 1)
        return overlap_area

    def evaluate_placement_quality(self, chip_positions):
        total_wiring_cost = 0
        for (chip1, chip2) in self.connections:
            wire_cost = self.compute_wire_distance(chip1, chip2, chip_positions[chip1], chip_positions[chip2])
            total_wiring_cost += wire_cost

        total_overlap_penalty = 0
        chip_list = sorted(self.chip_specs.keys())
        for i, chip_a in enumerate(chip_list):
            for chip_b in chip_list[i+1:]:
                overlap = self.calculate_overlap_area(chip_a, chip_b, chip_positions[chip_a], chip_positions[chip_b])
                if overlap > 0:
                    total_overlap_penalty += overlap

        total_score = total_wiring_cost + total_overlap_penalty
        return total_score, total_wiring_cost, total_overlap_penalty

    def optimize_placement(self, initial_positions, max_iterations=1000, patience=50):
        print("Starting chip placement optimization...")
        print("This might take a moment as we explore different arrangements...")

        current_positions = initial_positions.copy()
        current_score = self.evaluate_placement_quality(current_positions)[0]

        self.score_timeline = [current_score]
        self.optimization_history = []

        iteration_count = 0
        stagnation_counter = 0

        print(f"Starting score: {current_score}")
        print("Searching for better arrangements...")

        while iteration_count < max_iterations and stagnation_counter < patience:
            iteration_count += 1

            best_improvement = 0
            best_move_details = None
            best_new_arrangement = None

            for chip_id in self.chip_specs.keys():
                min_x, max_x = self.calculate_movement_boundaries(chip_id)
                current_x = current_positions[chip_id]

                if current_x > min_x:
                    test_positions = current_positions.copy()
                    test_positions[chip_id] = current_x - 1
                    test_score = self.evaluate_placement_quality(test_positions)[0]
                    improvement = current_score - test_score

                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_move_details = (chip_id, 'left', current_x - 1)
                        best_new_arrangement = test_positions

                if current_x < max_x:
                    test_positions = current_positions.copy()
                    test_positions[chip_id] = current_x + 1
                    test_score = self.evaluate_placement_quality(test_positions)[0]
                    improvement = current_score - test_score

                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_move_details = (chip_id, 'right', current_x + 1)
                        best_new_arrangement = test_positions

            if best_improvement > 0:
                current_positions = best_new_arrangement
                current_score -= best_improvement
                self.optimization_history.append((iteration_count, best_move_details, best_improvement))
                stagnation_counter = 0

                print(f"Step {iteration_count}: Moved chip {best_move_details[0]} {best_move_details[1]} " +
                      f"to position {best_move_details[2]}, improved score by {best_improvement:.1f}")
            else:
                stagnation_counter += 1
                if stagnation_counter == 1:
                    print(f"Step {iteration_count}: No beneficial moves found, continuing search...")

            self.score_timeline.append(current_score)

            if current_score == 0:
                print(f"Perfect solution found at step {iteration_count}!")
                break

        print(f"Optimization completed after {iteration_count} steps!")
        return current_positions, current_score


class ChipVisualizationTool:
    def __init__(self, optimizer):
        self.optimizer = optimizer

    def display_grid_layout(self, chip_positions, title="Chip Layout"):
        grid = np.zeros((self.optimizer.board_height, self.optimizer.board_width), dtype=object)

        for chip_id, x_position in chip_positions.items():
            y_position = self.optimizer.chip_specs[chip_id]['y']
            width = self.optimizer.chip_specs[chip_id]['w']
            height = self.optimizer.chip_specs[chip_id]['h']

            for row_offset in range(height):
                for col_offset in range(width):
                    grid_y = y_position + row_offset
                    grid_x = x_position + col_offset

                    if grid_y < self.optimizer.board_height and grid_x < self.optimizer.board_width:
                        if grid[grid_y, grid_x] == 0:
                            grid[grid_y, grid_x] = str(chip_id)
                        else:
                            grid[grid_y, grid_x] = f"{grid[grid_y, grid_x]}/{chip_id}"

        print(f"\n{title}:")
        for row_index in range(self.optimizer.board_height - 1, -1, -1):
            row_display = ""
            for col_index in range(self.optimizer.board_width):
                cell_content = grid[row_index, col_index]
                if cell_content == 0:
                    row_display += "  . "
                else:
                    row_display += f"{cell_content:>3} "
            print(f"y={row_index}: {row_display}")

        column_labels = "x:  " + "".join([f"{i:>4}" for i in range(self.optimizer.board_width)])
        print(column_labels)

    def create_progress_charts(self, initial_positions, final_positions, initial_score, final_score):
        initial_breakdown = self.optimizer.evaluate_placement_quality(initial_positions)
        final_breakdown = self.optimizer.evaluate_placement_quality(final_positions)

        plt.figure(figsize=(15, 5))

        # 1) Optimization Progress
        plt.subplot(1, 3, 1)
        plt.plot(self.optimizer.score_timeline, color='royalblue', linewidth=2,
                marker='o', markersize=4, label='Score')
        plt.xlabel('Optimization Step')
        plt.ylabel('Conflict Score (Lower is Better)')
        plt.title('Optimization Progress')
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color='red', linestyle='--', alpha=0.6, label='Perfect Score')
        plt.legend()

        # 2) Improvements per Move
        plt.subplot(1, 3, 2)
        if self.optimizer.optimization_history:
            step_numbers, move_details, improvements = zip(*self.optimizer.optimization_history)
            plt.bar(step_numbers, improvements, alpha=0.8, color='seagreen', width=0.8)
            plt.xlabel('Optimization Step')
            plt.ylabel('Score Improvement')
            plt.title('Improvements per Move')
            plt.grid(True, alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'No improvements\nwere possible',
                    ha='center', va='center', transform=plt.gca().transAxes)
            plt.title('Improvements per Move')

        # 3) Cost Breakdown
        plt.subplot(1, 3, 3)
        categories = ['Initial Setup', 'Final Result']
        wiring_costs = [initial_breakdown[1], final_breakdown[1]]
        overlap_penalties = [initial_breakdown[2], final_breakdown[2]]

        x_positions = range(len(categories))
        bar_width = 0.35

        plt.bar([i - bar_width/2 for i in x_positions], wiring_costs, bar_width,
                label='Wiring Cost', alpha=0.9, color='dodgerblue')
        plt.bar([i + bar_width/2 for i in x_positions], overlap_penalties, bar_width,
                label='Overlap Penalty', alpha=0.9, color='tomato')

        plt.xlabel('Optimization Stage')
        plt.ylabel('Cost Components')
        plt.title('Cost Breakdown')
        plt.xticks(x_positions, categories)
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def print_detailed_summary(self, initial_positions, final_positions, initial_score, final_score):
        print(f"\n" + "="*60)
        print(f"CHIP PLACEMENT OPTIMIZATION RESULTS")
        print(f"="*60)

        final_breakdown = self.optimizer.evaluate_placement_quality(final_positions)
        initial_breakdown = self.optimizer.evaluate_placement_quality(initial_positions)

        print(f"Performance Improvement:")
        print(f"   Initial score: {initial_breakdown[0]} (wiring: {initial_breakdown[1]}, overlaps: {initial_breakdown[2]})")
        print(f"   Final score:   {final_breakdown[0]} (wiring: {final_breakdown[1]}, overlaps: {final_breakdown[2]})")
        print(f"   Improvement:   {initial_breakdown[0] - final_breakdown[0]} points better!")

        print(f"\nOptimization Statistics:")
        print(f"   Total optimization steps: {len(self.optimizer.score_timeline) - 1}")
        print(f"   Successful improvements:  {len(self.optimizer.optimization_history)}")

        print(f"\nFinal Chip Positions:")
        position_data = []
        for chip_id in sorted(final_positions.keys()):
            position_data.append({
                'Chip': f'Chip-{chip_id}',
                'X': final_positions[chip_id],
                'Y': self.optimizer.chip_specs[chip_id]['y'],
                'Width': self.optimizer.chip_specs[chip_id]['w'],
                'Height': self.optimizer.chip_specs[chip_id]['h']
            })

        df = pd.DataFrame(position_data)
        print(df.to_string(index=False))
