
def run_game():
    
    import sys    
    import os    
    import shutil
    import subprocess
    import platform
    import time
    from core.learner import Learner
    from core.game import Game    
    from multiprocessing import Process, Queue
    from pathlib import Path
    from time import sleep
    from util.plot import start_plot
    from gui.window import start_gui        
    
    script_dir = Path(__file__).resolve().parent

    def print_state(game: Game):        
        current_os = platform.system()
        if current_os == "Windows":
            subprocess.run(["cls"], shell=True)
        elif current_os == "Linux":
            subprocess.run(["clear"])

        owners = game.get_owners(game.grid)
        for i in range(0, 36):
            if i % 6 == 0:
                print()            
            if game.grid[i].blocked:
                print(owners[i], end='\t')            
            else:
                print(f"({owners[i]})", end='\t')

        print('\n')
        print("player_rings:", game.player_rings, end=', ')
        print("turn:", game.turn, end=', ')
        print("end:", game.end, end=', ')
        print("winner:", game.winner, end=', ')
        print("step:", game.step)

        if game.end:
            if game.winner is None:
                print('tie')
            elif game.winner == Game.PLAYER_ONE:
                print('one')
            elif game.winner == Game.PLAYER_TWO:
                print('two')
            return True
        return False

    seed = 1
    using_gui = True

    learner = Learner()
    learner.load_q_table()

    if '-train' in sys.argv:
        rounds = int(input("Rounds: "))
        learner.train(rounds)
        learner.save_q_table()

    if '-test' in sys.argv:
        print('Range of minimax limit: ')        
        bottom = int(input('\tBottom limit (default=1, min=1): '))
        top = int(input('\tTop limit (default=5, max=10): '))
        if bottom < 1:
            bottom = 1
        if top > 10:
            top = 10
        test_load = int(input('Number of tests for each minimax limit (default=1): '))
        try:
            seed = int(input("Game seed (default=1): "))
        except:
            seed = 1

        test_path = f"{script_dir}/test"

        if os.path.exists(test_path) and os.path.isdir(test_path):
            shutil.rmtree(test_path)
        os.makedirs(test_path, exist_ok=True)

        total_time = 0
        
        with open(f'{test_path}/log.csv', 'w') as output_log:
            try:
                for alpha_beta_p1 in range(2):
                    for alpha_beta_p2 in range(2):
                        for limit_p1 in range(bottom, top + 1):
                            for limit_p2 in range(bottom, top + 1):                        
                                mean_time = 0
                                label = f's_{seed}_{"ab" if alpha_beta_p1 == 1 else "mm"}_{limit_p1}_x_{"ab" if alpha_beta_p2 else "mm"}_{limit_p2}'
                                for i in range(test_load):
                                    label_i = label + f"_{i+1}"
                                    tree_path = f'{test_path}/tree_{label_i}.xml'
                                    game = Game(seed=seed, xml_file_name=tree_path)
                                    params = {Game.PLAYER_ONE: [limit_p1, False], Game.PLAYER_TWO: [limit_p2, True]}
                                    start_time = time.perf_counter()
                                    while not game.end:
                                        position = game.calculate_best_play(game.turn, depth=params[game.turn][0], use_alpha_beta=params[game.turn][1])
                                        x, y = game.get_xy(position)
                                        game.place_ring(x, y)
                                    game.save_tree_xml()
                                    end_time = time.perf_counter()
                                    execution_time = end_time - start_time
                                    mean_time += execution_time
                                    total_time += execution_time
                                    output_log.write(f"{label_i} {execution_time:.6f} {game.winner} {len(game.state_tree.node_index.keys())}\n")                                
                                mean_time /= test_load                            
                                print(f"\nMean time for {label}: {mean_time:.6f} seconds")
            except:
                print("Execution stopped.")
            finally:                
                print(f"\nTotal Execution time: {total_time:.6f} seconds.\n")

        exit(0)
    if '-reset' in sys.argv and os.path.exists(f'{script_dir}/tree.xml'):
        os.remove(f'{script_dir}/tree.xml')
    
    if '-nogui' in sys.argv:
        using_gui = False

    
    autonomous_p1 = input("Autonomous player one? (y/n): ")[0] == "y"
    autonomous_p2 = input("Autonomous player two? (y/n): ")[0] == "y"

    if autonomous_p1:
        p1_learning = input("Autonomous player one learns? (y/n): ")[0] == "y"
    if autonomous_p2:
        p2_learning = input("Autonomous player two learns? (y/n): ")[0] == "y"

    p1_alpha_beta = False    
    p2_alpha_beta = False

    p1_expertise = 0
    p2_expertise = 0

    if autonomous_p1 and not p1_learning:        
        p1_alpha_beta = input("Autonomous player one uses alpha-beta? (y/n): ")[0] == "y"
    if autonomous_p2 and not p2_learning:    
        p2_alpha_beta = input("Autonomous player two uses alpha-beta? (y/n): ")[0] == "y"

    if autonomous_p1 and not p1_learning:
        p1_expertise = int(input("Autonomous player one expertise (Minimax limit): "))
    if autonomous_p2 and not p2_learning:
        p2_expertise = int(input("Autonomous player two expertise (Minimax limit): "))

    game = Game(seed=seed, xml_file_name=f'{script_dir}/tree.xml')
    
    print(f'{script_dir}/tree.xml')

    plot_p = Process(target=start_plot, args=(f'{script_dir}/tree.xml', 1000))
    plot_p.start()

    if using_gui:
        gui_input_queue = Queue()
        gui_output_queue = Queue()
        gui_p = Process(target=start_gui, args=(game.grid, gui_input_queue, gui_output_queue))        
        gui_p.start()

    sleep(1) 
    
    running = True
    while running:
        if using_gui:   
            while not gui_output_queue.empty():
                command, data = gui_output_queue.get_nowait()
                
                if command == 'CLICK' and not game.end:
                    if autonomous_p2 and game.turn == Game.PLAYER_ONE or autonomous_p1 and game.turn == Game.PLAYER_TWO or not autonomous_p1 and not autonomous_p2:
                        position = data                
                        x, y = game.get_xy(position)                                      
                        if game.place_ring(x, y):
                            print(f"Player {"one" if game.turn == Game.PLAYER_ONE else "two"} places donut: {position}")                        
                            gui_input_queue.put(('UPDATE', (game.grid, game.turn, game.winner, game.end, game.player_rings)))                        
                            if game.end:
                                print(f"Winner: {game.winner}")   
                            game.save_tree_xml()
                    
                elif command == 'UNDO':
                    print("Undoing last turn...")                    
                    if game.turn == Game.PLAYER_ONE and autonomous_p2 or game.turn == Game.PLAYER_TWO and autonomous_p1:
                        if game.last_state():
                            if game.last_state():
                                gui_input_queue.put(('UPDATE', (game.grid, game.turn, game.winner, game.end, game.player_rings)))
                    else:
                        if game.last_state():
                            gui_input_queue.put(('UPDATE', (game.grid, game.turn, game.winner, game.end, game.player_rings)))
                    game.save_tree_xml()

                elif command == 'QUIT':
                    running = False     

            if autonomous_p1 and game.turn == Game.PLAYER_ONE or autonomous_p2 and game.turn == Game.PLAYER_TWO: 
                if p1_learning or p2_learning:
                    sleep(0.5)
                else:
                    if autonomous_p1 and autonomous_p2:
                        sleep(0.5 / (min(p1_expertise, p2_expertise) + 0.1))
                    elif autonomous_p1 or autonomous_p2:
                        sleep(0.5 / (max(p1_expertise, p2_expertise) + 0.1))

                if autonomous_p1 and game.turn == Game.PLAYER_ONE:
                    if p1_learning and not game.end: 
                        position = learner.choose_action(learner.Q_TABLE, game, game.get_valid_moves(), 0)
                    else:
                        position = game.calculate_best_play(game.PLAYER_ONE, depth=p1_expertise, use_alpha_beta=p1_alpha_beta)
                else:
                    if p2_learning and not game.end:                        
                        position = learner.choose_action(learner.Q_TABLE, game, game.get_valid_moves(), 0)
                    else:
                        position = game.calculate_best_play(game.PLAYER_TWO, depth=p2_expertise, use_alpha_beta=p2_alpha_beta)

                if position != -1:
                    x, y = game.get_xy(position)  

                    if game.place_ring(x, y):
                        print(f"Player {"one" if game.turn == Game.PLAYER_ONE else "two"} places donut: {position}")
                        gui_input_queue.put(('UPDATE', (game.grid, game.turn, game.winner, game.end, game.player_rings)))
                        if game.end:
                            print(f"Winner: {game.winner}")          
                        game.save_tree_xml()                   

            if not gui_p.is_alive():
                running = False
        else:                                         
            print_state(game)
            if autonomous_p1:
                position = game.calculate_best_play(game.PLAYER_ONE, depth=p1_expertise, use_alpha_beta=p1_alpha_beta)
            else:
                position = int(input("p1: "))
            
            if position == -1:
                break

            x, y = game.get_xy(position) 

            if game.place_ring(x, y):
                print_state(game)                

                if autonomous_p2:
                    position = game.calculate_best_play(game.PLAYER_TWO, depth=p2_expertise, use_alpha_beta=p2_alpha_beta)
                else:
                    position = int(input("p2: "))

                if position != -1:
                    x, y = game.get_xy(position)                          
                    game.place_ring(x, y)
                game.save_tree_xml()

            if game.end:                
                running = False                                                    
    
    if plot_p.is_alive():
        print("Terminating Dash Server...")
        plot_p.terminate() 
        plot_p.join(timeout=2) 
        
        if plot_p.is_alive():          
            plot_p.kill()  

    if using_gui and gui_p.is_alive():
        print("Terminating GUI...")
        gui_p.terminate() 
        gui_p.join(timeout=2) 
        
        if gui_p.is_alive():          
            gui_p.kill()   

if __name__ == '__main__':    
    print('Warning: these dependencies are needed for this project: pygame, plotly, igraph, dash\n')
    run_game()