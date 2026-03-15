"""Initial migration - fresh start

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001_initial'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    op.execute("CREATE TYPE doctorstatus AS ENUM ('pending', 'approved', 'rejected', 'suspended')")
    op.execute("CREATE TYPE appointmentstatus AS ENUM ('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show')")
    op.execute("CREATE TYPE visittype AS ENUM ('online', 'offline')")
    op.execute("CREATE TYPE chatsessionstatus AS ENUM ('active', 'closed')")
    op.execute("CREATE TYPE chatsource AS ENUM ('web', 'mobile', 'admin')")
    op.execute("CREATE TYPE messagerole AS ENUM ('user', 'assistant', 'system')")
    op.execute("CREATE TYPE contenttype AS ENUM ('text', 'json', 'event')")
    op.execute("CREATE TYPE triagestatus AS ENUM ('success', 'failed')")
    op.execute("CREATE TYPE urgencylevel AS ENUM ('low', 'medium', 'high')")

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Specializations table
    op.create_table(
        'specializations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(120), nullable=False),
        sa.Column('slug', sa.String(120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_specializations_title', 'specializations', ['title'], unique=True)
    op.create_index('ix_specializations_slug', 'specializations', ['slug'], unique=True)

    # Doctors table
    op.create_table(
        'doctors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('experience_years', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('license_number', sa.String(100), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'approved', 'rejected', 'suspended', name='doctorstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('specialization_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['specialization_id'], ['specializations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('license_number')
    )

    # Schedules table
    op.create_table(
        'schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('slot_duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doctor_id', 'day_of_week', name='uq_schedule_doctor_day')
    )

    # Chat sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'closed', name='chatsessionstatus', create_type=False), nullable=False, server_default='active'),
        sa.Column('source', postgresql.ENUM('web', 'mobile', 'admin', name='chatsource', create_type=False), nullable=False, server_default='web'),
        sa.Column('locale', sa.String(10), nullable=True, server_default='ru'),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('context_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chat_sessions_user_created', 'chat_sessions', ['user_id', 'created_at'])
    op.create_index('ix_chat_sessions_status_updated', 'chat_sessions', ['status', 'updated_at'])

    # Chat messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', postgresql.ENUM('user', 'assistant', 'system', name='messagerole', create_type=False), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', postgresql.ENUM('text', 'json', 'event', name='contenttype', create_type=False), nullable=False, server_default='text'),
        sa.Column('model_name', sa.String(100), nullable=True),
        sa.Column('prompt_version', sa.String(50), nullable=True),
        sa.Column('token_input', sa.Integer(), nullable=True),
        sa.Column('token_output', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chat_messages_session_created', 'chat_messages', ['session_id', 'created_at'])

    # Triage runs table
    op.create_table(
        'triage_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', postgresql.ENUM('success', 'failed', name='triagestatus', create_type=False), nullable=False, server_default='success'),
        sa.Column('urgency', postgresql.ENUM('low', 'medium', 'high', name='urgencylevel', create_type=False), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('inputs_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('outputs_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('filters_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('model_name', sa.String(100), nullable=True),
        sa.Column('prompt_version', sa.String(50), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('token_input', sa.Integer(), nullable=True),
        sa.Column('token_output', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('trigger_message_id', sa.Integer(), nullable=True),
        sa.Column('recommended_specialization_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trigger_message_id'], ['chat_messages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recommended_specialization_id'], ['specializations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_triage_runs_session_created', 'triage_runs', ['session_id', 'created_at'])
    op.create_index('ix_triage_runs_specialization_created', 'triage_runs', ['recommended_specialization_id', 'created_at'])

    # Appointments table
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', postgresql.ENUM('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show', name='appointmentstatus', create_type=False), nullable=False, server_default='scheduled'),
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('visit_type', postgresql.ENUM('online', 'offline', name='visittype', create_type=False), nullable=False, server_default='offline'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('cancel_reason', sa.Text(), nullable=True),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('triage_run_id', sa.Integer(), nullable=True),
        sa.Column('rescheduled_from_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['triage_run_id'], ['triage_runs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['rescheduled_from_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_appointments_date_time', 'appointments', ['date_time'])
    op.execute("""
        CREATE UNIQUE INDEX ix_appointments_doctor_datetime_active
        ON appointments (doctor_id, date_time)
        WHERE status IN ('scheduled', 'confirmed')
    """)

    # Triage candidates table
    op.create_table(
        'triage_candidates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('matched_filters_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('triage_run_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['triage_run_id'], ['triage_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('triage_run_id', 'rank', name='uq_triage_candidate_run_rank'),
        sa.UniqueConstraint('triage_run_id', 'doctor_id', name='uq_triage_candidate_run_doctor')
    )
    op.create_index('ix_triage_candidates_run_rank', 'triage_candidates', ['triage_run_id', 'rank'])

    # Medical records table
    op.create_table(
        'medical_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('diagnosis', sa.Text(), nullable=False),
        sa.Column('prescription', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_medical_records_patient', 'medical_records', ['patient_id', 'created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('medical_records')
    op.drop_table('triage_candidates')
    op.drop_index('ix_appointments_doctor_datetime_active', table_name='appointments')
    op.drop_table('appointments')
    op.drop_table('triage_runs')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('schedules')
    op.drop_table('doctors')
    op.drop_table('specializations')
    op.drop_table('users')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS urgencylevel")
    op.execute("DROP TYPE IF EXISTS triagestatus")
    op.execute("DROP TYPE IF EXISTS contenttype")
    op.execute("DROP TYPE IF EXISTS messagerole")
    op.execute("DROP TYPE IF EXISTS chatsource")
    op.execute("DROP TYPE IF EXISTS chatsessionstatus")
    op.execute("DROP TYPE IF EXISTS visittype")
    op.execute("DROP TYPE IF EXISTS appointmentstatus")
    op.execute("DROP TYPE IF EXISTS doctorstatus")
