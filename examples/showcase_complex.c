/*
 * AI Compiler Showcase - Complex C Program
 * This program demonstrates advanced struct support, mixed data types,
 * complex expressions, and real-world C programming patterns.
 */

// Complex struct with mixed data types
struct GamePlayer
{
    int id;
    float health;
    double score;
    int level;
};

// Another struct for demonstration
struct Vector3D
{
    double x;
    double y;
    double z;
};

// Struct with different field types
struct GameState
{
    int round;
    float timeLeft;
    double totalScore;
};

int main()
{
    // Complex struct variable declarations
    struct GamePlayer player1;
    struct GamePlayer player2;
    struct Vector3D position;
    struct GameState game;

    // Initialize player 1 with complex expressions
    player1.id = 1001;
    player1.health = 100.0f;
    player1.score = 2500.75;
    player1.level = 5;

    // Initialize player 2
    player2.id = 1002;
    player2.health = 85.5f;
    player2.score = 3200.25;
    player2.level = 7;

    // Complex 3D vector operations
    position.x = 10.5;
    position.y = -5.25;
    position.z = 100.0;

    // Game state with floating point arithmetic
    game.round = 3;
    game.timeLeft = 45.5f;
    game.totalScore = player1.score + player2.score;

    // Complex member access and arithmetic
    player1.health = player1.health - 15.5f;
    player2.score = player2.score * 1.1;

    // Update position with complex calculations
    position.x = position.x + 5.0;
    position.y = position.y * 2.0;
    position.z = position.z - 10.5;

    // Advanced struct field manipulation
    game.timeLeft = game.timeLeft - 1.0f;
    game.totalScore = game.totalScore + 500.0;

    // Complex conditional-style expressions (simulated)
    player1.level = player1.level + 1;
    player2.level = player2.level + 2;

    // Final calculations
    game.round = game.round + 1;
    position.x = position.x + position.y;

    return 0;
}
